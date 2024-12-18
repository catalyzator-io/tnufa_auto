from src.utils.models import SectionInfo, Taxonomy

taxonomy: Taxonomy = {
  "TEAM_LEADERSHIP": [
    "founder", "team", "leadership", "expertise", "advisory board",
    "organizational structure", "academic affiliations", "key team members",
    "management", "experience", "background", "skills", "research affiliations",
    "board members", "executives", "directors", "advisors", "professors"
  ],
  "COMPANY_FUNDAMENTALS": [
    "company", "registration", "history", "mission", "vision",
    "location", "headquarters", "incorporation", "company profile",
    "business description", "founding date", "company timeline",
    "physical location", "branch offices", "corporate identity",
    "business registration", "company structure"
  ],
  "PRODUCT_TECHNOLOGY": [
    "technology", "product", "service", "development stage",
    "technical architecture", "unique selling proposition", "IP",
    "innovation", "features", "specifications", "technical details",
    "product roadmap", "technology stack", "core technology",
    "product pipeline", "R&D", "intellectual property", "patents",
    "technical capabilities", "product differentiation"
  ],
  "MARKET_ANALYSIS": [
    "market size", "TAM", "SAM", "SOM", "target market",
    "market segments", "competition", "competitive landscape",
    "market trends", "industry analysis", "market dynamics",
    "entry barriers", "geographic focus", "market opportunity",
    "market research", "industry trends", "market validation",
    "competitor analysis", "market penetration"
  ],
  "BUSINESS_MODEL": [
    "revenue streams", "pricing strategy", "distribution channels",
    "customer acquisition", "partnership strategy", "cost structure",
    "business strategy", "go-to-market", "sales channels",
    "revenue model", "monetization", "pricing model",
    "distribution strategy", "sales strategy", "partnerships",
    "business operations", "operational model"
  ],
  "TRACTION_VALIDATION": [
    "customers", "users", "pilot programs", "letters of intent",
    "partnerships", "market validation", "revenue metrics",
    "user growth", "customer testimonials", "case studies",
    "proof of concept", "pilot results", "early adopters",
    "customer feedback", "market traction", "validation results",
    "success stories", "client portfolio"
  ],
  "FINANCIAL_INFORMATION": [
    "funding requirements", "use of funds", "financial projections",
    "runway", "funding rounds", "financial metrics", "revenue",
    "costs", "burn rate", "cash flow", "balance sheet",
    "income statement", "financial model", "investment needs",
    "funding history", "valuation", "cap table", "financial planning"
  ],
  "DEVELOPMENT_EXECUTION": [
    "product roadmap", "R&D milestones", "go-to-market strategy",
    "scaling plans", "risk mitigation", "development timeline",
    "execution strategy", "growth strategy", "expansion plans",
    "operational roadmap", "development phases", "milestone planning",
    "risk assessment", "strategic planning", "implementation plan"
  ],
  "LEGAL_COMPLIANCE": [
    "IP rights", "patents", "regulatory requirements", "compliance",
    "legal structure", "licensing", "agreements", "contracts",
    "regulatory approvals", "certifications", "legal documentation",
    "compliance requirements", "regulatory framework", "legal status",
    "intellectual property rights", "trademark", "copyright"
  ],
  "IMPACT_INNOVATION": [
    "social impact", "environmental impact", "innovation",
    "technology advantages", "industry contribution", "sustainability",
    "social responsibility", "environmental benefits", "SDGs",
    "innovation metrics", "impact measurement", "social value",
    "environmental sustainability", "innovation framework"
  ],
}

section_info: SectionInfo = {
  "Introduction": "Who is presenting, the company name, and a concise overview of the idea or value proposition.",
  "The Problem": "Articulate the specific pain point or challenge the startup aims to solve, with evidence or context if available.",
  "The Need": "Highlight the unmet customer needs or gaps in the market that justify the solution.",
  "The Solution": "Detail the solution, emphasizing its unique selling propositions (USPs) and competitive advantages.",
  "The Business Model": "Describe the revenue streams, pricing strategy, customer acquisition channels, and overall business strategy.",
  "Go-to-Market Strategy": "Explain the approach for market entry, customer engagement, and scaling.",
  "Market Opportunity": "Summarize the target market, including total addressable market (TAM), serviceable addressable market (SAM), market growth potential, and industry trends.",
  "Technology/Innovation": "Provide insights into the underlying technology, product features, technical architecture, or innovative aspects of the solution.",
  "Competitive Analysis": "Compare with competitors, addressing differentiators, competitive landscape, and barriers to entry.",
  "Traction and Validation": "Include existing metrics, milestones, customer testimonials, pilot programs, or validation efforts.",
  "Team and Leadership": "Evaluate the team's qualifications, expertise, organizational structure, and any notable advisors or affiliations.",
  "Financial Information": "Cover funding requirements, revenue forecasts, financial health, use of funds, and return on investment (ROI).",
  "Development and Execution": "Outline the product roadmap, scaling strategy, risk management, and execution plan.",
  "Legal and Compliance": "Note IP rights, regulatory requirements, certifications, and any legal aspects.",
  "Impact and Innovation": "Discuss social, environmental, or economic impacts, sustainability, and contributions to innovation.",
  "Additional Supporting Information": "Include insights from supplementary materials like pitch decks, business plans, technical documents, or financial models.",
}