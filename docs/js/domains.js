/**
 * Domain metadata catalog for the Texas Insurance Practice Exam.
 * Maps each question domain to descriptions, exam outline sections, and subdomain info.
 * Based on the Texas Insurance Examination Content Outlines (effective December 1, 2025).
 */

const DOMAIN_CATALOG = {
  "Types of Policies": {
    description: "Covers the full range of life and health insurance products: traditional whole life, universal/variable/indexed life, term life, annuities, combination plans, disability income, medical expense (HMO, PPO, POS), Medicare supplements, long-term care, and specialty policies (dental, vision, critical illness).",
    outlineSections: [
      "Life: I — Types of Policies (15 Qs)",
      "L&H: I — Life Types of Policies (15 Qs)",
      "L&H: V — Health Types of Policies (16 Qs)"
    ]
  },

  "Policy Riders, Provisions, Options, and Exclusions": {
    description: "Covers policy riders (waiver of premium, guaranteed insurability, AD&D, term riders, LTC, disability), standard life provisions (entire contract, beneficiary designations, premium payment, reinstatement, nonforfeiture, dividends, incontestability, assignments, settlement options), health provisions (mandatory and optional), exclusions, and rights of renewability.",
    outlineSections: [
      "Life: II — Policy Riders, Provisions, Options & Exclusions (15 Qs)",
      "L&H: II — Life Policy Riders/Provisions (15 Qs)",
      "L&H: VI — Health Policy Provisions, Clauses & Riders (15 Qs)"
    ]
  },

  "Completing the Application, Underwriting, and Delivering the Policy": {
    description: "Covers the application process (required signatures, changes, warranties/representations, initial premium collection, receipts), replacement rules, point-of-sale disclosures (HIPAA, HIV consent), USA PATRIOT Act/AML, GLBA privacy, underwriting (insurable interest, medical info, Fair Credit Reporting Act, risk classification, STOLI/IOLI), policy delivery, and contract law fundamentals.",
    outlineSections: [
      "Life: III — Completing the Application, Underwriting & Delivering (12 Qs)",
      "L&H: III — Same (12 Qs)",
      "L&H: IX — Field Underwriting Procedures (8 Qs)"
    ]
  },

  "Taxes, Retirement, and Other Insurance Concepts": {
    description: "Covers third-party ownership, life settlements, group life (conversion, contributory vs. noncontributory), qualified and nonqualified retirement plans, life insurance needs analysis (personal and business: key person, buy-sell), Social Security benefits, tax treatment of premiums/proceeds/dividends, Modified Endowment Contracts (MECs), and health-related tax concepts (FSAs, HSAs, HRAs).",
    outlineSections: [
      "Life: IV — Retirement & Other Insurance Concepts (8 Qs)",
      "L&H: IV — Same (8 Qs)",
      "L&H: VII — Social Insurance (6 Qs)",
      "L&H: VIII — Other Insurance Concepts (5 Qs)"
    ]
  },

  "Policy Provisions": {
    description: "Focuses specifically on standard policy provisions found in life and health contracts: free look period, grace period, entire contract clause, incontestability, reinstatement, policy loans, nonforfeiture options, beneficiary designations, assignment, suicide clause, misstatement of age/gender, settlement options, and accelerated death benefits.",
    outlineSections: [
      "Life: II.B — Policy Provisions & Options",
      "L&H: VI.A-B — Mandatory & Optional Health Provisions"
    ]
  },

  "Life Insurance": {
    description: "Covers life insurance product knowledge in depth: whole life cash value mechanics, term vs. permanent life comparisons, universal and variable life features, annuity types and taxation, dividend options, riders (AD&D, waiver of premium), group life, settlement options, Modified Endowment Contracts, backdating, and contract law principles specific to life insurance.",
    outlineSections: [
      "Life: I — Types of Life Policies",
      "Life: II — Life Policy Riders & Provisions",
      "L&H: I-II — Life Product Knowledge"
    ]
  },

  "Health Insurance": {
    description: "Covers all health insurance products and concepts: HMOs (referrals, utilization review, complaints/appeals), PPOs, POS plans, disability income, COBRA continuation, coordination of benefits, Medicare supplements, long-term care, pre-existing conditions, renewability provisions, proof of loss, subrogation, and managed care principles.",
    outlineSections: [
      "L&H: V — Health Types of Policies (16 Qs)",
      "L&H: VI — Health Policy Provisions & Riders (15 Qs)",
      "L&H: VII — Social Insurance / Medicare (6 Qs)",
      "L&H: VIII — Other Health Insurance Concepts (5 Qs)"
    ]
  },

  "Texas State Statutes Common to All Lines": {
    description: "Covers Texas-specific statutes and rules that apply to both life and health insurance: Commissioner of Insurance powers (examination, investigation, penalties, cease and desist), insurance definitions (certificate of authority, foreign/domestic/alien, stock/mutual, fraternals), licensing requirements (types, exemptions, appointment, CE, records, denial/revocation), unfair trade practices (false advertising, misrepresentation, rebating, fraud, boycott, commingling, discrimination), agent duties, and the Texas Life and Health Guaranty Association.",
    outlineSections: [
      "Life State Specific: I — TX Statutes Common to Life & Health (20 Qs)",
      "L&H State Specific: I — TX Statutes Common to Life & Health (14 Qs)"
    ]
  },

  "Texas State Statutes Pertaining to Life, Health, and HMOs": {
    description: "Covers Texas statutes specific to individual lines: Life — advertising/illustrations, policy summary/buyer's guide, free look, grace period, policy loans, prohibited provisions, group life eligibility/conversion/assignment, credit life, replacement duties, nonforfeiture law. Health — newborn coverage, chemical dependency, Medicare supplement standards, AIDS testing, long-term care, small group health, Affordable Care Act (exchanges, subsidies, essential benefits, employer responsibilities). HMOs — definitions, evidence of coverage, nonrenewal/cancellation, enrollment, out-of-network claims.",
    outlineSections: [
      "Life State Specific: II — TX Statutes Pertinent to Life Only (10 Qs)",
      "L&H State Specific: II — TX Statutes Pertinent to Life Only (6 Qs)",
      "L&H State Specific: III — TX Statutes Pertinent to Health Only (7 Qs)",
      "L&H State Specific: IV — TX Statutes Pertinent to HMOs (3 Qs)"
    ]
  },

  "Texas Statutes": {
    description: "Covers additional Texas regulatory topics: agent authority and licensing, continuing education requirements, insurer classification (foreign/domestic/alien, stock/mutual), TDI complaints process, HMO regulation and independent review, and the Texas Life and Health Guaranty Association protections.",
    outlineSections: [
      "Life State Specific: I-II (various sections)",
      "L&H State Specific: I-IV (various sections)"
    ]
  },

  "Agent Duties": {
    description: "Covers the legal duties and responsibilities of insurance agents in Texas: replacement notification requirements under TIC Chapter 1114, commission sharing rules, fiduciary obligations, records maintenance, and required disclosures to applicants when existing coverage is being replaced.",
    outlineSections: [
      "Life State Specific: I.E — Agent Duties/Responsibilities",
      "L&H State Specific: I.E — Agent Duties/Responsibilities",
      "Life State Specific: II.F — Replacement Duties"
    ]
  },

  "Underwriting and Delivery": {
    description: "Covers the underwriting and policy delivery process: insurable interest requirements, conditional vs. binding receipts, HIPAA privacy disclosures, adverse selection, Stranger/Investor-Owned Life Insurance (STOLI/IOLI), risk classification, and the agent's responsibilities when delivering a policy to the client.",
    outlineSections: [
      "Life: III — Completing the Application & Underwriting",
      "L&H: IX — Field Underwriting Procedures (8 Qs)"
    ]
  },

  "Unfair Trade Practices": {
    description: "Covers prohibited trade practices under Texas insurance law: misrepresentation, twisting (inducing replacement through misrepresentation), churning (excessive replacement for commissions), rebating, commingling of funds, defamation of competitors, unfair claims settlement practices, and unfair discrimination in insurance transactions.",
    outlineSections: [
      "Life State Specific: I.D — Marketing Practices / Unfair Trade Practices",
      "L&H State Specific: I.D — Marketing Practices / Unfair Trade Practices"
    ]
  }
};

/**
 * Dynamically compute subdomain counts from QUESTION_BANK.
 * Returns { [domain]: { [subdomain]: count } }
 */
function getDomainSubdomainCounts() {
  const map = {};
  QUESTION_BANK.forEach(q => {
    if (!map[q.domain]) map[q.domain] = {};
    if (!map[q.domain][q.subdomain]) map[q.domain][q.subdomain] = 0;
    map[q.domain][q.subdomain]++;
  });
  return map;
}
