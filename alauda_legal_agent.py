#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alauda Global Legal Agent - 合同风险审核自动化脚本
===============================================
为 Alauda (灵雀云) 法务团队提供基于 AI 的自动化合同审核方案。

核心功能:
- 自动提取合同关键条款
- 根据 Alauda 标准红线进行风险判定
- 输出 Mode A (对比表) 和 Mode B (修订建议文本)
"""

import re
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ReviewItem:
    """审核条目数据类"""
    category: str
    category_cn: str
    original_clause: str
    risk_level: str
    risk_icon: str
    benchmark_requirement: str
    standard_clause: str
    rationale: str


class AlaudaLegalAgent:
    """Alauda 全球法律与运营架构师 Agent"""
    
    def __init__(self):
        """初始化 Alauda 的核心审核标准 (对标 Red Hat ECA)"""
        
        # 核心红线知识库 - 基于 Alauda 商业风险过滤标准
        self.benchmark = {
            "subscription_metrics": {
                "keywords": [
                    r"subscription", r"metric", r"unit", r"unlimited\s+use", r"enterprise[- ]wide", r"site\s+license"
                ],
                "redline": "订阅应基于具体计量单位(Unit)而非无限制使用",
                "standard_clause": "Subscription pricing is determined by counting Units (e.g., Node, Core/vCPU) as defined in the relevant Product Appendix. Client must purchase the appropriate quantity of Subscriptions.",
                "rationale": "基于节点/核心的订阅模式，确保商业收益匹配实际消耗",
                "risk_rules": {
                    "high": [
                        (r"unlimited\s+(use|deployment|access|install)", "要求无限制使用或部署权"),
                        (r"enterprise[- ]wide\s+(license|subscription|use)", "要求企业级统一授权"),
                    ],
                    "medium": [
                        (r"site\s+license", "站点级授权 (可能导致计量失控)"),
                    ]
                }
            },
            
            "liability": {
                "keywords": [
                    r"liability", r"indemnif", r"limitation", 
                    r"maximum aggregate", r"cap", r"liable"
                ],
                "redline": "赔偿限额：订阅服务为12个月费用，EULA免费软件为50美元",
                "standard_clause": "For Subscriptions, Supplier's total aggregate liability shall not exceed the total fees paid in the 12 months preceding the claim. For Software under EULA, liability is capped at US$50.",
                "rationale": "符合 Alauda 与主流厂商 (如 Red Hat/SUSE) 的双轨制商业风险对冲标准",
                "risk_rules": {
                    "high": [
                        (r"3\s*times", "赔偿倍数过高 (3倍)"),
                        (r"unlimited\s+liability", "无赔偿上限"),
                        (r"direct\s*,\s*indirect\s*,\s*incidental", "赔偿范围过宽"),
                    ],
                    "medium": [
                        (r"(?!12\s*months?)\d+\s*months?", "赔偿期限非12个月标准"),
                    ]
                }
            },
            
            "ipr": {
                "keywords": [
                    r"intellectual\s*property", r"ownership", r"derivative\s*works?",
                    r"new\s*materials", r"work\s*for\s*hire", r"all\s*rights",
                    r"foreground", r"background"
                ],
                "redline": "保留核心平台及衍生作品所有权",
                "standard_clause": "Alauda retains all rights to the pre-existing platform (PaaS) and any derivative works based on its core technology. Customer owns only custom components developed specifically for Customer.",
                "rationale": "保护核心产品分发权，避免被单一银行绑定",
                "risk_rules": {
                    "high": [
                        (r"customer\s+owns\s+all\s+(rights?\s+)?(derivative|new)", "客户拥有所有衍生作品权利"),
                        (r"work\s*for\s*hire", "适用雇佣作品条款"),
                        (r"all\s+intellectual\s+property\s+(developed|created)\s+shall\s+belong\s+to\s+customer", "所有开发IP归属客户"),
                    ],
                    "medium": [
                        (r"joint\s+ownership", "共同所有权条款"),
                    ]
                }
            },
            
            "acceptance": {
                "keywords": [
                    r"acceptance", r"test\s*plan", r"reject", r"deemed",
                    r"verification", r"sign.?off", r"approval"
                ],
                "redline": "10个工作日默示验收",
                "standard_clause": "Deliverables are deemed accepted if no written rejection is received within 10 business days of delivery.",
                "rationale": "解决现金流被流程拖延的问题",
                "risk_rules": {
                    "high": [
                        (r"written\s+approval\s+(is\s+)?required", "需要书面批准"),
                        (r"customer.{0,20}satisfaction", "以客户满意为准"),
                    ],
                    "medium": [
                        (r"(?!10\s*(business\s+)?days?)\d+\s*(business\s+)?days?", "验收期非10天标准"),
                        (r"no\s+deemed\s+acceptance", "无默示验收条款"),
                    ]
                }
            },
            
            "termination": {
                "keywords": [
                    r"terminat", r"cancel", r"expire", r"end\s+date",
                    r"notice\s+period", r"for\s+convenience"
                ],
                "redline": "合理终止通知期 (30-90天)",
                "standard_clause": "Either party may terminate this Agreement for convenience upon 30 days' prior written notice. For material breach, the non-breaching party may terminate upon 30 days' notice if breach remains uncured.",
                "rationale": "保持业务灵活性",
                "risk_rules": {
                    "high": [
                        (r"terminat\w*\s+for\s+any\s+reason\s+immediately", "可立即终止"),
                        (r"no\s+termination\s+(right|for\s+convenience)", "无便利终止权"),
                    ],
                    "medium": [
                        (r"\d{3,}\s*days?\s+(prior\s+)?notice", "通知期过长 (≥100天)"),
                    ]
                }
            },
            
            "governing_law": {
                "keywords": [
                    r"governing\s+law", r"jurisdiction", r"venue",
                    r"dispute\s+resolut", r"arbitration", r"litigation"
                ],
                "redline": "适用法律需考虑司法管辖区差异",
                "standard_clause": "This Agreement shall be governed by the laws of [Jurisdiction]. Any disputes shall be resolved in the courts of [Venue].",
                "rationale": "不同法域适用不同条款标准",
                "risk_rules": {
                    "high": [
                        (r"exclusive\s+jurisdiction\s+of\s+customer", "客户专属管辖"),
                    ],
                    "medium": [
                        (r"arbitration\s+(is\s+)?required", "强制仲裁条款"),
                    ]
                }
            },
            
            "data_protection": {
                "keywords": [
                    r"data\s+protection", r"privacy", r"gdpr", r"pdpa",
                    r"personal\s+data", r"data\s+processing", r"confidential"
                ],
                "redline": "符合适用数据保护法规",
                "standard_clause": "Each party shall comply with applicable data protection laws, including but not limited to PDPA and GDPR where applicable.",
                "rationale": "合规风险控制",
                "risk_rules": {
                    "high": [
                        (r"supplier\s+(shall\s+be\s+)?solely\s+responsible", "供应商独自承担数据责任"),
                        (r"unlimited\s+indemnif.*data", "数据赔偿无上限"),
                    ],
                    "medium": [
                        (r"data\s+controller", "数据控制者身份认定"),
                    ]
                }
            },
            
            # ========== 技术支持合同专项审核维度 ==========
            
            "sla_response": {
                "keywords": [
                    r"response\s*time", r"resolution\s*time", r"sla", r"service\s*level",
                    r"24/7", r"24\s*\*\s*7", r"severity\s*level", r"priority\s*level",
                    r"within\s*\d+", r"target\s*time", r"initial\s*response"
                ],
                "redline": "SLA 响应时间需符合公司最新运营标准",
                "standard_clause": "Response times: P1 (Critical): 30 minutes initial response; P2 (High): 2 hours; P3 (Medium): 4 hours; P4 (Low): 8 hours. Resolution times to be determined on a best-effort basis.",
                "rationale": "确保向客户承诺的 SLA 不超过运维团队可支撑的最高标准",
                "risk_rules": {
                    "high": [
                        (r"within\s*(10|15|20)\s*(minutes|mins)", "响应时间极短 (<30分钟)"),
                        (r"within\s*1\s*\(?\w*\)?\s*(hour|hr)", "响应时间极短 (可能违背 P2/P3/P4 标准)"),
                        (r"guarantee\s*\d+\s*(hour|day)\s*resolution", "保证解决时间"),
                        (r"24/7\s*support", "24/7 全天候支持承诺"),
                    ],
                    "medium": [
                        (r"within\s*[2-3]\s*\(?\w*\)?\s*(hours|hrs)", "响应时间较短 (可能违背 P3/P4 标准)"),
                        (r"response\s*time.{0,20}\d+\s*(hour|minute)", "明确响应时间承诺"),
                    ]
                }
            },
            
            "support_scope": {
                "keywords": [
                    r"warranty\s*support", r"technical\s*support", r"support\s*scope",
                    r"shall\s*(provide|offer|deliver)\s*support", r"support\s*include",
                    r"support\s*services?\s*(shall|will|include)", r"подержк", r"гарантий"
                ],
                "redline": "明确支持范围与排除项(拒绝驻场及定制开发)",
                "standard_clause": "Support includes: bug fixes, security patches, and remote technical assistance for supported versions. Support excludes: custom development, on-site support, third-party products not certified by Alauda, and issues caused by Customer's modifications or unsupported environments.",
                "rationale": "防止支持范围无限扩大，匹配 Alauda 标准服务基线",
                "risk_rules": {
                    "high": [
                        (r"unlimited\s*support", "无限制支持"),
                        (r"any\s*and\s*all\s*(issues|problems|requests)", "任何和所有问题"),
                        (r"support\s*(shall|will)\s*(include|cover)\s*all", "支持涵盖所有"),
                        (r"resolve\s*any\s*issue", "解决任何问题"),
                        (r"on-site\s+support", "包含现场/驻场支持"),
                        (r"custom\s*(code|development)", "包含定制代码开发"),
                    ],
                    "medium": [
                        (r"no\s*(limit|cap|exclusion)", "无限制或排除条款"),
                        (r"other\s*types?\s*of\s*support\s*as\s*set\s*forth", "支持范围可能扩展"),
                        (r"third[- ]party\s+(products?|software)", "包含第三方产品支持(可能未认证)"),
                    ]
                }
            },
            
            "exclusion_liability": {
                "keywords": [
                    r"not\s*(be\s*)?(liable|responsible)", r"exclusion", r"disclaimer",
                    r"indirect\s*(damage|loss)", r"consequential", r"incidental",
                    r"data\s*(loss|damage)", r"business\s*interruption",
                    r"solely\s*responsible", r"no\s*liability", r"without\s*limitation"
                ],
                "redline": "明确排除间接损失/数据损失责任",
                "standard_clause": "In no event shall Alauda be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation loss of profits, data, use, or goodwill, regardless of the form of action.",
                "rationale": "保护供应商免受无限赔偿责任",
                "risk_rules": {
                    "high": [
                        (r"liable\s*for\s*(all|any)\s*(damages?|losses?)", "对所有损失承担责任"),
                        (r"without\s*limitation\s*to\s*(damages?|liability)", "责任无限制"),
                        (r"responsible\s*for\s*(data|all)\s*(loss|damage)", "对数据损失负责"),
                    ],
                    "medium": [
                        (r"full\s*indemnif", "完全赔偿"),
                        (r"no\s*exclusion\s*of\s*consequential", "未排除间接损失"),
                    ]
                }
            },
            
            "training_commitment": {
                "keywords": [
                    r"training", r"education", r"learning", r"instruction",
                    r"hours?\s*(of\s*)?training", r"обучен",
                    r"provide\s*training", r"conduct\s*training", r"training\s*(hours|sessions)"
                ],
                "redline": "培训承诺需有上限",
                "standard_clause": "Alauda will provide up to 40 hours of online training per year. Additional training may be purchased at agreed rates. Training content and schedule to be mutually agreed.",
                "rationale": "避免培训成本失控",
                "risk_rules": {
                    "high": [
                        (r"\d{3,}\s*\(?\w*\)?.*?hours?\s*(of\s*)?training", "培训时长过长 (≥100小时)"),
                        (r"unlimited\s*training", "无限制培训"),
                        (r"training\s*on\s*any\s*(topic|subject)", "任何主题培训"),
                    ],
                    "medium": [
                        (r"(72|70|80|60)\s*\([^)]*\).*?hours?\s*per\s*calendar\s*year", "培训时长较多 (60-80小时/年)"),
                        (r"(72|70|80|60)\s*hours?\s*(per\s*year|annually|per\s*calendar\s*year)", "培训时长较多 (60-80小时/年)"),
                        (r"training\s*on\s*any\s*software.related", "任何软件相关培训"),
                        (r"request\s*training\s*on\s*any", "可请求任何培训"),
                    ]
                }
            },
            
            "support_duration": {
                "keywords": [
                    r"warranty\s*(support|period)", r"support\s*(period|duration|term)",
                    r"years?\s*from\s*(the\s*)?(release|delivery)", r"support\s*for\s*\d+\s*years?",
                    r"maintain\s*support", r"continue\s*support", r"обеспечива.*поддержк",
                    r"гарантийн.*поддержк"
                ],
                "redline": "支持期限需可控 (建议 1-2 年)",
                "standard_clause": "Warranty support is provided for the current major version and one prior major version, for a maximum of 18 months from general availability of the new major version.",
                "rationale": "控制长期维护成本",
                "risk_rules": {
                    "high": [
                        (r"\d{3,}\s*years?\s*(from|of|support)", "支持期限过长 (≥3年)"),
                        (r"lifetime\s*support", "终身支持"),
                        (r"in\s*perpetuity", "永久支持"),
                        (r"obligated?\s*to\s*continue\s*support", "有义务继续支持"),
                    ],
                    "medium": [
                        (r"2\s*years?\s*(from|of|support)", "支持期限为 2 年"),
                        (r"throughout\s*the\s*entire\s*term", "整个合同期间支持"),
                        (r"continue\s*warranty\s*support\s*for\s*previously\s*received", "继续支持旧版本"),
                    ]
                }
            },
            
            "access_rights": {
                "keywords": [
                    r"access\s*(to|right)", r"grant\s*access", r"remote\s*access",
                    r"screen.?shar", r"video.?confer", r"direct\s*access",
                    r"it\s*infrastructure", r"system\s*access", r"доступ"
                ],
                "redline": "限制访问权限 (仅屏幕共享)",
                "standard_clause": "Support is provided remotely via screen sharing session arranged by Customer. Supplier shall not have direct access to Customer's IT infrastructure, systems, or data. Customer controls all access and may redact sensitive information.",
                "rationale": "保护客户安全，降低供应商风险",
                "risk_rules": {
                    "high": [
                        (r"direct\s*access\s*to\s*(customer|system|infrastructure)", "直接访问客户系统"),
                        (r"full\s*access\s*to", "完全访问"),
                        (r"unrestricted\s*access", "无限制访问"),
                        (r"remote\s*access\s*to\s*(server|database|production)", "远程访问生产环境"),
                    ],
                    "medium": [
                        (r"access\s*to\s*(source\s*code|database|configuration)", "访问源代码/数据库"),
                    ]
                }
            },
            
            "termination_support": {
                "keywords": [
                    r"terminat\w*\s*(support|warranty)", r"cease\s*support", 
                    r"discontinue\s*support", r"end\s*of\s*support", r"sunset",
                    r"notify\s*\d+\s*(days?|months?)", r"прекращ.*поддержк",
                    r"early\s*termination", r"premature\s*termination",
                    r"reject.*terminat", r"refuse.*terminat"
                ],
                "redline": "终止支持需合理通知期",
                "standard_clause": "Either party may terminate support services upon 90 days' prior written notice. Upon termination, Customer may continue using the Software but without warranty support or updates.",
                "rationale": "保持业务灵活性",
                "risk_rules": {
                    "high": [
                        (r"terminat\w*\s*without\s*notice", "无通知终止"),
                        (r"immediate\s*terminat", "立即终止"),
                        (r"no\s*right\s*to\s*terminat", "无终止权"),
                        (r"obligated?\s*to\s*continue\s*support", "被迫继续支持"),
                    ],
                    "medium": [
                        (r"\d{3,}\s*days?\s*(prior\s*)?notice", "通知期过长 (≥100天)"),
                        (r"(customer|mws|client).{0,30}(reject|refuse).{0,30}terminat", "客户可拒绝终止"),
                        (r"right\s*to\s*reject.*terminat", "客户有权拒绝终止"),
                    ]
                }
            }
        }
        
        # 风险等级图标
        self.risk_icons = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "N/A": "⚪"
        }
    
    def extract_clauses(self, text: str) -> List[Tuple[str, str]]:
        """
        将合同文本拆分为逻辑段落
        返回: [(条款编号, 条款内容)]
        """
        clauses = []
        
        # 匹配条款编号模式 - 支持多种格式
        patterns = [
            # 标准格式: 1.1, 1.1.1, 2.1.1
            r'(\d+\.\d+(?:\.\d+)?)\s+(.+?)(?=\n\d+\.\d+|\n[A-Z][A-Z\s]{5,}|$)',
            # 字母格式: A.1, B.2
            r'([A-Z]\.\d+)\s+(.+?)(?=\n[A-Z]\.\d+|\n\d+\.\d+|$)',
            # Article/Section 格式
            r'(Article\s+\d+|Section\s+\d+)\s*[:\.]?\s*(.+?)(?=Article\s+\d+|Section\s+\d+|$)',
            # 列表格式: 1), 2), 3.1), 2.1.1)
            r'(\d+(?:\.\d+)*(?:\))?)\s*([A-ZА-Я][^.]{50,1500}?)(?=\n\d+(?:\.\d+)*\)|$)',
            # 俄语列表格式
            r'(\d+(?:\.\d+)*)\s*([А-ЯA-Z][^0-9]{50,1500}?)(?=\n\d+(?:\.\d+)+|\n[A-ZА-Я][a-zа-я]{2,}|\n\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for num, content in matches:
                content = content.strip()
                if len(content) > 30:  # 过滤太短的片段
                    # 清理内容
                    content = re.sub(r'\s+', ' ', content)
                    clauses.append((num.strip(), content))
        
        # 如果没有匹配到编号，按段落分割
        if not clauses:
            paragraphs = re.split(r'\n\s*\n|\n(?=[A-ZА-Я][a-zа-я]+(?:ing|ion|ment|ity|ова)\s)', text)
            for i, p in enumerate(paragraphs, 1):
                p = p.strip()
                p = re.sub(r'\s+', ' ', p)
                if len(p) > 80:
                    clauses.append((str(i), p))
        
        # 去重
        seen = set()
        unique_clauses = []
        for num, content in clauses:
            key = content[:100]
            if key not in seen:
                seen.add(key)
                unique_clauses.append((num, content))
        
        return unique_clauses
    
    def check_risk(self, category: str, text: str) -> Tuple[str, str]:
        """
        根据规则判定风险等级
        返回: (风险等级, 风险原因)
        """
        config = self.benchmark.get(category)
        if not config:
            return "N/A", "未配置审核规则"
        
        text_lower = text.lower()
        risk_rules = config.get("risk_rules", {})
        
        # 检查高风险规则
        for pattern, reason in risk_rules.get("high", []):
            if re.search(pattern, text_lower):
                return "HIGH", reason
        
        # 检查中等风险规则
        for pattern, reason in risk_rules.get("medium", []):
            if re.search(pattern, text_lower):
                return "MEDIUM", reason
        
        # 检查是否包含关键词
        keywords = config.get("keywords", [])
        keyword_found = any(re.search(kw, text_lower) for kw in keywords)
        
        if keyword_found:
            return "LOW", "符合 Alauda 标准"
        
        return "N/A", "未检测到相关条款"
    
    def analyze_contract(self, contract_text: str) -> List[ReviewItem]:
        """
        分析合同文本，生成审核报告
        """
        clauses = self.extract_clauses(contract_text)
        report = []
        
        # 中文类别名称映射
        category_names = {
            # 销售合同审核维度
            "subscription_metrics": "订阅计量 (Subscription Metrics)",
            "liability": "赔偿条款 (Liability)",
            "ipr": "知识产权 (IP)",
            "acceptance": "验收条款 (Acceptance)",
            "termination": "终止条款 (Termination)",
            "governing_law": "适用法律 (Governing Law)",
            "data_protection": "数据保护 (Data Protection)",
            # 技术支持合同审核维度
            "sla_response": "SLA 响应时间 (SLA Response)",
            "support_scope": "支持范围 (Support Scope)",
            "exclusion_liability": "责任排除 (Exclusion of Liability)",
            "training_commitment": "培训承诺 (Training Commitment)",
            "support_duration": "支持期限 (Support Duration)",
            "access_rights": "访问权限 (Access Rights)",
            "termination_support": "支持终止 (Support Termination)"
        }
        
        for category, config in self.benchmark.items():
            found_clauses = []  # 收集所有匹配的条款
            
            # 搜索包含关键词的条款
            for num, text in clauses:
                if any(re.search(kw, text, re.IGNORECASE) for kw in config["keywords"]):
                    found_clauses.append((num, text))
            
            # 同时在整个合同文本中搜索风险规则
            risk_level, risk_reason = "LOW", "符合 Alauda 标准"
            triggered_clause = None
            triggered_num = ""
            
            # 在整个合同中检测风险
            text_lower = contract_text.lower()
            risk_rules = config.get("risk_rules", {})
            
            # 检查高风险规则
            for pattern, reason in risk_rules.get("high", []):
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    risk_level = "HIGH"
                    risk_reason = reason
                    # 找到包含这个匹配的条款
                    matched_text = match.group()
                    for num, text in found_clauses:
                        if matched_text.lower() in text.lower():
                            triggered_clause = text
                            triggered_num = num
                            break
                    # 如果没在已匹配条款中找到，在整个合同中定位
                    if not triggered_clause:
                        # 提取匹配位置周围的上下文
                        pos = contract_text.lower().find(matched_text.lower())
                        if pos >= 0:
                            start = max(0, pos - 100)
                            end = min(len(contract_text), pos + len(matched_text) + 200)
                            triggered_clause = contract_text[start:end].strip()
                            triggered_num = "§"
                    break
            
            # 检查中等风险规则
            if risk_level == "LOW":
                for pattern, reason in risk_rules.get("medium", []):
                    match = re.search(pattern, text_lower, re.IGNORECASE)
                    if match:
                        risk_level = "MEDIUM"
                        risk_reason = reason
                        # 找到包含这个匹配的条款
                        matched_text = match.group()
                        for num, text in found_clauses:
                            if matched_text.lower() in text.lower():
                                triggered_clause = text
                                triggered_num = num
                                break
                        # 如果没在已匹配条款中找到，在整个合同中定位
                        if not triggered_clause:
                            pos = contract_text.lower().find(matched_text.lower())
                            if pos >= 0:
                                start = max(0, pos - 100)
                                end = min(len(contract_text), pos + len(matched_text) + 200)
                                triggered_clause = contract_text[start:end].strip()
                                triggered_num = "§"
                        break
            
            # 如果没有触发风险但有匹配的条款，使用第一个
            if not triggered_clause and found_clauses:
                triggered_num, triggered_clause = found_clauses[0]
            
            # 如果有匹配的条款或触发了风险，添加到报告
            if triggered_clause or found_clauses:
                if not triggered_clause:
                    triggered_num, triggered_clause = found_clauses[0]
                
                # 截断过长的条款
                display_clause = triggered_clause
                if len(display_clause) > 250:
                    display_clause = display_clause[:250] + "..."
                
                item = ReviewItem(
                    category=category.upper(),
                    category_cn=category_names.get(category, category),
                    original_clause=f"[{triggered_num}] {display_clause}",
                    risk_level=risk_level,
                    risk_icon=self.risk_icons.get(risk_level, "⚪"),
                    benchmark_requirement=config["redline"],
                    standard_clause=config["standard_clause"],
                    rationale=f"{config['rationale']} - {risk_reason}"
                )
                report.append(item)
        
        return report
    
    def generate_markdown(self, analysis: List[ReviewItem], 
                          include_mode_b: bool = True) -> str:
        """
        生成 Markdown 格式的审核报告
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"""# 🚀 Alauda Legal Review Report

> **生成时间**: {timestamp}  
> **审核标准**: Alauda Global Legal Benchmark (对标 Red Hat ECA)

---

## 📊 Mode A: 风险对比表

| 监控维度 | 原文摘要 | 风险等级 | Alauda 标准要求 | 风险原因 |
| :--- | :--- | :---: | :--- | :--- |
"""
        
        for item in analysis:
            md += f"| **{item.category_cn}** | {item.original_clause[:80]}... | {item.risk_icon} {item.risk_level} | {item.benchmark_requirement} | {item.rationale} |\n"
        
        if include_mode_b:
            md += "\n---\n\n## ✍️ Mode B: 建议修订文本\n\n"
            md += "> 以下为符合 Alauda 标准的修订建议，可直接用于回复客户\n\n"
            
            for item in analysis:
                if item.risk_level in ["HIGH", "MEDIUM"]:
                    md += f"""### {item.category_cn}

**❌ 原条款风险**: {item.rationale}

**✅ 建议修订**:
```
{item.standard_clause}
```

---
"""
        
        # 添加摘要统计
        high_count = sum(1 for item in analysis if item.risk_level == "HIGH")
        medium_count = sum(1 for item in analysis if item.risk_level == "MEDIUM")
        low_count = sum(1 for item in analysis if item.risk_level == "LOW")
        
        md += f"""
---

## 📈 审核摘要

| 风险等级 | 数量 |
| :---: | :---: |
| 🔴 高风险 | {high_count} |
| 🟡 中风险 | {medium_count} |
| 🟢 低风险 | {low_count} |

"""
        
        return md
    
    def generate_json(self, analysis: List[ReviewItem]) -> str:
        """生成 JSON 格式的审核报告"""
        result = {
            "metadata": {
                "agent": "Alauda Global Legal Agent",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            },
            "summary": {
                "total_issues": len(analysis),
                "high_risk": sum(1 for item in analysis if item.risk_level == "HIGH"),
                "medium_risk": sum(1 for item in analysis if item.risk_level == "MEDIUM"),
                "low_risk": sum(1 for item in analysis if item.risk_level == "LOW")
            },
            "findings": [
                {
                    "category": item.category,
                    "category_cn": item.category_cn,
                    "original_clause": item.original_clause,
                    "risk_level": item.risk_level,
                    "benchmark_requirement": item.benchmark_requirement,
                    "standard_clause": item.standard_clause,
                    "rationale": item.rationale
                }
                for item in analysis
            ]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


def read_contract_file(file_path: str) -> str:
    """读取合同文件 (支持 .txt, .md, .json)"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    suffix = path.suffix.lower()
    
    if suffix in [".txt", ".md"]:
        return path.read_text(encoding="utf-8")
    
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("text", data.get("contract", ""))
    
    else:
        # 尝试作为纯文本读取
        return path.read_text(encoding="utf-8")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Alauda Global Legal Agent - 合同风险审核工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 直接审核合同文本
  python alauda_legal_agent.py -t "合同文本..."
  
  # 从文件读取合同
  python alauda_legal_agent.py -f contract.txt
  
  # 输出 JSON 格式
  python alauda_legal_agent.py -f contract.txt -o json
  
  # 保存报告到文件
  python alauda_legal_agent.py -f contract.txt --output report.md
        """
    )
    
    parser.add_argument("-t", "--text", type=str, help="直接输入合同文本")
    parser.add_argument("-f", "--file", type=str, help="从文件读取合同")
    parser.add_argument("-o", "--format", choices=["markdown", "json"], 
                        default="markdown", help="输出格式 (默认: markdown)")
    parser.add_argument("--output", type=str, help="保存报告到指定文件")
    parser.add_argument("--no-mode-b", action="store_true", 
                        help="不包含 Mode B 修订建议")
    
    args = parser.parse_args()
    
    # 获取合同文本
    if args.text:
        contract_text = args.text
    elif args.file:
        contract_text = read_contract_file(args.file)
    else:
        # 使用示例合同
        contract_text = """
        14.3 Supplier Entities' total liability to DBS Entities is limited to 3 times all amounts paid 
        under this Agreement in the 12 months preceding the claim.
        
        11.1 DBS owns all rights, title and interest in and to Intellectual Property Rights developed 
        including all derivative works and enhancements.
        
        4.3 DBS will carry out Acceptance Tests within 30 days and notify the Supplier if the 
        Deliverables are Accepted or rejected. Customer's written approval is required for final acceptance.
        
        18.1 Either party may terminate this Agreement for convenience upon 180 days' prior written notice.
        
        22.1 This Agreement shall be governed by the laws of Singapore and subject to the exclusive 
        jurisdiction of the Singapore courts.
        """
        print("⚠️  未提供合同文本，使用示例合同进行演示\n")
    
    # 执行分析
    agent = AlaudaLegalAgent()
    analysis = agent.analyze_contract(contract_text)
    
    # 生成报告
    if args.format == "json":
        report = agent.generate_json(analysis)
    else:
        report = agent.generate_markdown(analysis, include_mode_b=not args.no_mode_b)
    
    # 输出结果
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"✅ 报告已保存至: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
