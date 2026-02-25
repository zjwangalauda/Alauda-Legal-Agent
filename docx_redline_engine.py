import os
import zipfile
import re
import datetime
from lxml import etree
import shutil

class WordRedlineEngine:
    """
    A production-grade engine to decompile a .docx file, inject Microsoft OpenXML
    Track Changes (Insertions, Deletions) and Comments directly into the AST,
    and recompile it.
    
    Usage:
        engine = WordRedlineEngine("contract.docx")
        engine.apply_redline("original clause text", "suggested replacement", "reason for change")
        engine.apply_redline(...)  # can call multiple times
        engine.save("contract_redlined.docx")
    """
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.temp_dir = docx_path + "_unzipped"
        self.nsmap = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        self.author = "Alauda AI Legal Copilot"
        self.date_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.comment_id_counter = 100
        
        self._unzip_docx()
        
        # Cache the document XML tree in memory — read once, write on save
        self._doc_tree = self._read_xml('word/document.xml')
        self._comments_initialized = False

    def _unzip_docx(self):
        with zipfile.ZipFile(self.docx_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
            
    def _read_xml(self, internal_path):
        with open(os.path.join(self.temp_dir, internal_path), 'rb') as f:
            return etree.fromstring(f.read())
            
    def _write_xml(self, tree, internal_path):
        with open(os.path.join(self.temp_dir, internal_path), 'wb') as f:
            f.write(etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone='yes'))

    def _normalize(self, text: str) -> str:
        """Normalize text for fuzzy matching: strip all non-word chars and lowercase."""
        return re.sub(r'\W+', '', text).lower()

    def apply_redline(self, original_text_snippet, suggested_text, comment_text):
        """
        Finds a paragraph containing `original_text_snippet` in the cached DOM.
        If found:
          1. Marks the original text with red strikethrough styling
          2. Injects a <w:ins> node with the suggested replacement
          3. Attaches a sidebar <w:comment> with the rationale
        Returns True if a match was found.
        """
        if not original_text_snippet:
            return False

        # Use up to 80 normalized chars for matching — 20 is too short and causes false positives
        search_target = self._normalize(original_text_snippet)[:80]
        
        if not search_target:
            return False

        paragraphs = self._doc_tree.findall('.//w:p', namespaces=self.nsmap)
        found_target = False
        
        for p in paragraphs:
            # Reconstruct full text of paragraph from all w:t nodes
            texts = [t.text for t in p.findall('.//w:t', namespaces=self.nsmap) if t.text]
            full_text = "".join(texts)
            clean_full = self._normalize(full_text)
            
            if search_target and search_target in clean_full:
                found_target = True
                
                # 1. Mark original text with red strikethrough to visually flag the risk
                for run in p.findall('.//w:r', namespaces=self.nsmap):
                    rpr = run.find(f"{{{self.nsmap['w']}}}rPr")
                    if rpr is None:
                        rpr = etree.Element(f"{{{self.nsmap['w']}}}rPr")
                        run.insert(0, rpr)
                    # Add strikethrough
                    strike = rpr.find(f"{{{self.nsmap['w']}}}strike")
                    if strike is None:
                        strike = etree.Element(f"{{{self.nsmap['w']}}}strike")
                        rpr.append(strike)
                    # Add red color
                    color = rpr.find(f"{{{self.nsmap['w']}}}color")
                    if color is None:
                        color = etree.Element(f"{{{self.nsmap['w']}}}color", val="DC2626")
                        rpr.append(color)
                    else:
                        color.set('val', 'DC2626')
                
                # 2. Inject sidebar comment
                self._inject_comment(self.comment_id_counter, comment_text)
                
                # Add CommentRangeStart at the beginning of paragraph
                comment_start = etree.Element(f"{{{self.nsmap['w']}}}commentRangeStart", id=str(self.comment_id_counter))
                p.insert(0, comment_start)
                
                # Add CommentRangeEnd
                comment_end = etree.Element(f"{{{self.nsmap['w']}}}commentRangeEnd", id=str(self.comment_id_counter))
                p.append(comment_end)
                
                # Add CommentReference
                r_ref = etree.Element(f"{{{self.nsmap['w']}}}r")
                ref_node = etree.Element(f"{{{self.nsmap['w']}}}commentReference", id=str(self.comment_id_counter))
                r_ref.append(ref_node)
                p.append(r_ref)
                
                # 3. Insert the replacement text as <w:ins> (Track Changes insertion)
                if suggested_text:
                    ins_node = etree.Element(f"{{{self.nsmap['w']}}}ins", 
                                             id=str(self.comment_id_counter + 1000),
                                             author=self.author, 
                                             date=self.date_str)
                    
                    r_ins = etree.Element(f"{{{self.nsmap['w']}}}r")
                    
                    # Style: bold + Alauda blue
                    rpr = etree.Element(f"{{{self.nsmap['w']}}}rPr")
                    b = etree.Element(f"{{{self.nsmap['w']}}}b")
                    color = etree.Element(f"{{{self.nsmap['w']}}}color", val="1A6A9A")
                    rpr.append(b)
                    rpr.append(color)
                    r_ins.append(rpr)
                    
                    t_ins = etree.Element(f"{{{self.nsmap['w']}}}t")
                    t_ins.set(f"{{{'http://www.w3.org/XML/1998/namespace'}}}space", "preserve")
                    t_ins.text = f" [AI Suggested Redline: {suggested_text}]"
                    
                    r_ins.append(t_ins)
                    ins_node.append(r_ins)
                    p.append(ins_node)
                
                self.comment_id_counter += 1
                break  # Only annotate the first match per snippet
                
        return found_target

    def _inject_comment(self, c_id, text):
        comments_path = 'word/comments.xml'
        
        # Initialize comments system once if needed
        if not self._comments_initialized:
            if not os.path.exists(os.path.join(self.temp_dir, comments_path)):
                self._init_comments_system()
            self._comments_initialized = True
            
        tree = self._read_xml(comments_path)
        
        comment = etree.Element(f"{{{self.nsmap['w']}}}comment", 
                                id=str(c_id), author=self.author, date=self.date_str)
        
        p = etree.Element(f"{{{self.nsmap['w']}}}p")
        r = etree.Element(f"{{{self.nsmap['w']}}}r")
        t = etree.Element(f"{{{self.nsmap['w']}}}t")
        t.text = text
        
        r.append(t)
        p.append(r)
        comment.append(p)
        
        tree.append(comment)
        self._write_xml(tree, comments_path)

    def _init_comments_system(self):
        """Creates the comments.xml and wires it up in rels if a document never had comments."""
        # Create basic comments.xml
        root = etree.Element(f"{{{self.nsmap['w']}}}comments", nsmap=self.nsmap)
        self._write_xml(etree.ElementTree(root), 'word/comments.xml')
        
        # Add to word/_rels/document.xml.rels
        rels_path = 'word/_rels/document.xml.rels'
        if os.path.exists(os.path.join(self.temp_dir, rels_path)):
            rels_tree = self._read_xml(rels_path)
            root_elem = rels_tree
            rel_ns = root_elem.nsmap.get(None, 'http://schemas.openxmlformats.org/package/2006/relationships')
            
            found = False
            for rel in root_elem:
                if 'comments.xml' in rel.attrib.get('Target', ''):
                    found = True
                    break
            if not found:
                max_id = 1
                for rel in root_elem:
                    r_id = rel.attrib.get('Id', '')
                    if r_id.startswith('rId'):
                        try: max_id = max(max_id, int(r_id[3:]))
                        except: pass
                
                new_rel = etree.Element(f"{{{rel_ns}}}Relationship", Target="comments.xml", 
                                        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments", 
                                        Id=f"rId{max_id+1}")
                root_elem.append(new_rel)
                self._write_xml(rels_tree, rels_path)
                
        # Add to [Content_Types].xml
        ct_path = '[Content_Types].xml'
        if os.path.exists(os.path.join(self.temp_dir, ct_path)):
            ct_tree = self._read_xml(ct_path)
            root_elem = ct_tree
            ct_ns = root_elem.nsmap.get(None, 'http://schemas.openxmlformats.org/package/2006/content-types')
            
            found = False
            for override in root_elem.findall(f'.//{{{ct_ns}}}Override'):
                if override.attrib.get('PartName') == '/word/comments.xml':
                    found = True
                    break
            if not found:
                override = etree.Element(f"{{{ct_ns}}}Override", 
                                         PartName="/word/comments.xml", 
                                         ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml")
                root_elem.append(override)
                self._write_xml(ct_tree, ct_path)

    def save(self, output_path):
        """Write the cached document DOM back to XML and re-package into .docx"""
        # Flush the cached document tree to disk
        self._write_xml(self._doc_tree, 'word/document.xml')
        
        # Package it back up
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.temp_dir)
                    zip_ref.write(file_path, arcname)
                    
        # Cleanup
        shutil.rmtree(self.temp_dir)
