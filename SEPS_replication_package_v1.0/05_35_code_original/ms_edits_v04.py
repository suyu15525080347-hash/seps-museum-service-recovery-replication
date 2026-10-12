# -*- coding: utf-8 -*-
"""Text edits v0.3 -> v0.4 (figure integration). Every edit is (old, new); old must occur exactly once."""
PH = {  # placeholder paragraphs (markdown form without ** **)
 '[Figure 0 about here: source-audited decision-support workflow]':
   'The workflow, from source audit to set-valued state, is summarised in Supplementary Fig. S1.',
 '[Table 2 and Figure 1 about here: museum endpoint recovery and real GIA context]':
   '[Table 2 and Figure 1 about here: geography and mission profiles of FY2024/25 recovery]',
 '[Table 3 and Figures 2–3 about here: scalar benchmarks and set-valued states]':
   '[Table 3 and Figures 2–3 about here: masking of the weakest mission and set-valued states]',
 '[Figure 4 about here: five-year mission recovery AUC by museum group]':
   '[Figure 4 about here: long-run mission strips and five-year recovery AUC]',
}
EDITS = [
 # abstract (kept <= 250 words; checked in QA)
 ('We examine this problem using newly released official data for museums and museum groups sponsored by the UK Department for Culture, Media and Sport (DCMS). The source workbooks provide institution-level Grant-in-Aid and performance series from 2008/09 to 2024/25.',
  'We examine this problem using newly released official DCMS data for the UK\'s sponsored national museums, with institution-level Grant-in-Aid and performance series from 2008/09 to 2024/25.'),
 ('formal education and organised youth participation are the most frequent bottlenecks.',
  'formal education and organised youth participation are the most frequent bottlenecks, whereas total attendance is weakest in only two cases.'),
 ('The result persists under alternative baselines, mission removal, recovery caps and a pre-pandemic normal-period comparison.',
  'The result persists under alternative baselines, mission removal and recovery caps, and late-recovery masking (0.217) is nearly double that in the same museums\' pre-pandemic normal years (0.122).'),
 # introduction
 ('Formal education and organised under-18 participation, rather than total attendance, are the most frequent bottlenecks.',
  'Formal education and organised under-18 participation, rather than total attendance, are the most frequent bottlenecks; total attendance is the weakest mission in only two cases.'),
 ('alternative treatment of above-baseline recovery, and exclusion of the two most disrupted shutdown years.',
  'alternative treatment of above-baseline recovery, and exclusion of the two most disrupted shutdown years. In the same museums, mean masking in late recovery (0.217) is close to twice its level in pre-pandemic normal years (0.122).'),
 # results 3.3
 ('UK loan venues in nine, total visits in two and under-16 visits in two.',
  'UK loan venues in nine, total visits in two and under-16 visits in two. Figure 2 displays all 50 cases: because the weakest mission can never exceed the average, every point lies on or below the diagonal, and its vertical distance from the diagonal is the masking span. Visitor-only masking is more dispersed than equal-weight masking (Fig. 2B).'),
 ('the 50 museum-years divide into 23 RED, 25 AMBER and two GREEN cases.',
  'the 50 museum-years divide into 23 RED, 25 AMBER and two GREEN cases. Figure 3B traces how the scalar verdicts map onto these states: four of the six equal-weight passes and ten of the twelve visitor-only passes are AMBER, while 21 of the 44 equal-weight failures would pass under some admissible weighting. Requiring each mission to receive at least 5% or 10% weight reduces the AMBER count at (τ=.90) from 25 to 17 and nine, respectively (Fig. 3C).'),
 # results 3.5
 ('The median weakest-mission five-year attainment is 0.3737 in both specifications.',
  'The median weakest-mission five-year attainment is 0.3737 in both specifications.\n\nFigure 4 places this window within the longer official series. In FY2020/21 the four attendance and learning series average between 0.03 and 0.09 of baseline across the ten groups, whereas UK loan venues average 0.69. The subsequent recoveries diverge by mission: by FY2024/25 mean capped attainment is 0.85 for total visits and 0.84 for under-16 visits, compared with 0.80 for formal education, 0.71 for UK loan venues and 0.66 for organised on-site under-18 participation (Fig. 5A). Weakest-mission five-year attainment ranges from 0.157 to 0.563 across the ten groups (Fig. 4B).'),
 # results 3.8
 ('The .90 distribution is 12 RED, 17 AMBER and four GREEN across 33 museum-years.',
  'The .90 distribution is 12 RED, 17 AMBER and four GREEN across 33 museum-years. Mean masking is higher in late recovery than in the normal years for nine of the eleven museums (Fig. 5B).'),
 ('the aggregation problem persists after the two most disrupted shutdown years are removed.',
  'the aggregation problem persists after the two most disrupted shutdown years are removed.\n\n**[Figure 5 about here: recovery paths and same-museum normal-period contrast]**'),
 # discussion
 ('A footfall-centred dashboard can therefore improve while a less visible public-service dimension remains materially below its own baseline.',
  'A footfall-centred dashboard can therefore improve while a less visible public-service dimension remains materially below its own baseline. Figures 1 and 4 make this pattern visible for individual groups and years rather than only in portfolio averages.'),
 ('yet still shows materially greater masking than the pre-COVID normal-period check.',
  'yet still shows materially greater masking than the pre-COVID normal-period check (0.217 versus 0.122).'),
 ('they omit visitor experience, opening hours, collection condition, digital access, accessibility quality, research and many curatorial activities.',
  'they omit visitor experience, opening hours, collection condition, digital access, accessibility quality, research and many curatorial activities. The maps in Figure 1 locate sites for orientation only and do not imply site-level recovery estimates.'),
 # conclusion
 ('The missions recovered at different rates, and total attendance was rarely the weakest dimension.',
  'The missions recovered at different rates, and total attendance was the weakest dimension in only two of 50 cases.'),
 ('The result persisted under alternative baselines, omission of each mission, relaxed recovery caps and exclusion of the two most disrupted shutdown years.',
  'The result persisted under alternative baselines, omission of each mission, relaxed recovery caps and exclusion of the two most disrupted shutdown years, and masking in late recovery was nearly twice that in the same museums\' pre-pandemic normal years.'),
]
NEW_PARAS = [  # (anchor text that ends the paragraph after which to insert, new paragraph)
 ('The study therefore emphasises descriptive and robustness comparisons rather than population-level inferential claims.',
  'Figure 1 adds a display-only geographic layer. Each group is drawn at one anchor site, with its other operating sites linked to it; coordinates are taken from Wikidata (property P625) and drawn on Greater London Authority borough and River Thames layers, Office for National Statistics local-authority and country boundaries (December 2024) and OpenStreetMap roads, parks and water. Site locations enter no calculation: all recovery, masking and Grant-in-Aid quantities remain measured at museum-group level.'),
 ('Two of 13 institutions with valid loan data restore UK loan venues to baseline.',
  'Figure 1 places the ten groups with complete five-mission data on their city geography. In FY2024/25 their weakest mission is organised on-site under-18 participation in five groups, formal education in two, UK loan venues in two and under-16 visits in one; only the British Museum has all five missions at or above 0.90 of baseline. Nine of the ten have real GIA at or above the FY2018/19 level, so the map juxtaposes resource context and service shortfall without implying a funding effect.'),
]
