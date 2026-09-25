
**A. Versions of the fusion result recomputed (all 150 patients, 50 progressors)**

| version | n | events | head_alone | head_ci | fuse2 | fuse3 | fuse3_ci | gain | gain_ci | perm_p_gain | third_arm |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v1_p32b_fields6_logistic | 150 | 50 | 0.738 | [0.652, 0.817] | 0.783 | 0.832 | [0.762, 0.894] | 0.05 | [0.015, 0.089] | 0.0025 | CV logistic on 6 imputed fields (incl-overlap heads) |
| v2_p32b_grade_only | 150 | 50 | 0.756 | [0.661, 0.842] | 0.783 | 0.851 | [0.781, 0.909] | 0.069 | [0.024, 0.119] | 0.0055 | imputed grade LGD+ (incl-overlap head) |
| v3_noov_fields2_logistic | 150 | 50 | 0.754 | [0.664, 0.834] | 0.783 | 0.846 | [0.774, 0.908] | 0.063 | [0.02, 0.107] | 0.0025 | CV logistic on 2 leak-free imputed fields (grade, inflammation) |
| v4_noov_grade_only_CANONICAL | 150 | 50 | 0.753 | [0.659, 0.84] | 0.783 | 0.85 | [0.779, 0.909] | 0.067 | [0.022, 0.114] | 0.003 | imputed grade LGD+ (leak-free head, 55 ERIN ids / 54 SWG patients excluded) |


**C. Subgroup characterisation (patient level)**

| variable | type | also_in_ERIN_54 | never_in_ERIN_96 | test | p |
|---|---|---|---|---|---|
| n_rows | continuous (median [IQR]) | 4 [2, 7] (n=54) | 3 [2, 6] (n=96) | Mann-Whitney | 0.25 |
| first_year | continuous (median [IQR]) | 2008 [2005, 2012] (n=54) | 2008 [2002, 2010] (n=96) | Mann-Whitney | 0.068 |
| span_days | continuous (median [IQR]) | 119 [0, 1548] (n=54) | 360 [0, 1536] (n=96) | Mann-Whitney | 0.954 |
| biopsies_total | continuous (median [IQR]) | 2 [1, 5] (n=54) | 3 [1, 5] (n=96) | Mann-Whitney | 0.484 |
| followup_months_first_to_last_biopsy | continuous (median [IQR]) | 24.6 [0, 69.6] (n=54) | 36.0 [0, 75.1] (n=96) | Mann-Whitney | 0.609 |
| days_first_to_event | continuous (median [IQR]) | 942 [434, 1894] (n=14) | 1102 [812, 2308] (n=36) | Mann-Whitney | 0.483 |
| age_at_diagnosis | continuous (median [IQR]) | 56.5 [51.2, 63.8] (n=22) | 65.0 [58.8, 68.2] (n=44) | Mann-Whitney | 0.006 |
| prague_C | continuous (median [IQR]) | 0 [0, 2.5] (n=20) | 0 [0, 2] (n=32) | Mann-Whitney | 0.76 |
| prague_M | continuous (median [IQR]) | 4.5 [4, 5.75] (n=22) | 4 [2, 6] (n=33) | Mann-Whitney | 0.27 |
| n_reads_mean | continuous (median [IQR]) | 22197935 [20800968, 25242923] (n=25) | 20981523 [18806932, 23508466] (n=56) | Mann-Whitney | 0.054 |
| cellularity_mean | continuous (median [IQR]) | 29.3 [23.9, 50.0] (n=5) | 47.5 [44.6, 50.0] (n=13) | Mann-Whitney | 0.34 |
| cx_max | continuous (median [IQR]) | 14.5 [0, 45.0] (n=54) | 11.5 [0, 46.5] (n=96) | Mann-Whitney | 0.911 |
| noise_mapd_mean | continuous (median [IQR]) | 0.0715 [0.0633, 0.0783] (n=54) | 0.074 [0.0645, 0.0821] (n=96) | Mann-Whitney | 0.246 |
| n_segments_mean | continuous (median [IQR]) | 218 [174, 291] (n=54) | 201 [162, 283] (n=96) | Mann-Whitney | 0.499 |
| frac_altered_0p15_mean | continuous (median [IQR]) | 0.0316 [0.0231, 0.0463] (n=54) | 0.031 [0.0208, 0.0531] (n=96) | Mann-Whitney | 0.92 |
| frac_altered_0p30_mean | continuous (median [IQR]) | 0.0151 [0.0146, 0.0158] (n=54) | 0.0152 [0.0148, 0.0169] (n=96) | Mann-Whitney | 0.078 |
| slide_age_at_scan_days_mean | continuous (median [IQR]) | 2823 [1424, 3650] (n=54) | 3057 [2237, 4031] (n=96) | Mann-Whitney | 0.044 |
| scan_year_first | continuous (median [IQR]) | 2017 [2017, 2017] (n=54) | 2017 [2017, 2017] (n=96) | Mann-Whitney | 0.45 |
| mpp_mean | continuous (median [IQR]) | 0.221 [0.221, 0.221] (n=54) | 0.221 [0.221, 0.221] (n=96) | Mann-Whitney | 0.194 |
| y | categorical (counts) | {0: 40, 1: 14} | {0: 60, 1: 36} | Fisher exact | 0.206 |
| baseline_grade | categorical (counts) | {0: 41, 1: 7, 2: 6} | {0: 80, 1: 6, 2: 10} | chi-square (3 levels; Fisher only defined for 2x2) | 0.359 |
| max_grade | categorical (counts) | {0: 36, 1: 6, 2: 12} | {0: 61, 1: 9, 2: 26} | chi-square (3 levels; Fisher only defined for 2x2) | 0.787 |
| endpoint_label_name | categorical (counts) | {'HGD': 8, 'IMC/cancer': 2, 'LGD (second consecutive)': 4, 'missing': 40} | {'HGD': 18, 'IMC/cancer': 8, 'LGD (second consecutive)': 10, 'missing': 60} | chi-square (4 levels; Fisher only defined for 2x2) | 0.484 |
| sex_demographics | categorical (counts) | {'F': 5, 'M': 17, 'missing': 32} | {'F': 10, 'M': 34, 'missing': 52} | chi-square (3 levels; Fisher only defined for 2x2) | 0.834 |
| gender_id_code | categorical (counts) | {'1': 40, '2': 14, 'missing': 0} | {'1': 74, '2': 21, 'missing': 1} | chi-square (3 levels; Fisher only defined for 2x2) | 0.655 |
| smoking | categorical (counts) | {'N': 4, 'Y': 10, 'missing': 40} | {'N': 4, 'Y': 17, 'missing': 75} | chi-square (3 levels; Fisher only defined for 2x2) | 0.681 |
| referral_hospital_db | categorical (counts) | {'Addenbrookes': 3, 'Bedford': 0, 'Hinchingbrooke': 0, 'None': 33, 'Not Specified': 18, 'West Suffolk': 0, 'not in DB': 0} | {'Addenbrookes': 2, 'Bedford': 1, 'Hinchingbrooke': 3, 'None': 55, 'Not Specified': 30, 'West Suffolk': 1, 'not in DB': 4} | chi-square (7 levels; Fisher only defined for 2x2) | 0.375 |
| seq_sheet_mode | categorical (counts) | {'discovery_777': 25, 'validation_268': 29} | {'discovery_777': 57, 'validation_268': 39} | Fisher exact | 0.129 |
| seq_batch_mode | categorical (counts) | {'Batch 1': 2, 'Batch 2': 3, 'Batch 3': 5, 'Batch 4': 2, 'Batch 5': 2, 'Batch 6': 4, 'Batch 8': 4, 'Batch 9': 1, 'Exome Subcohort': 1, 'NP Pilot Study': 1, 'Progressor Pilot Study': 0, 'missing': 29} | {'Batch 1': 6, 'Batch 2': 5, 'Batch 3': 6, 'Batch 4': 12, 'Batch 5': 9, 'Batch 6': 3, 'Batch 8': 7, 'Batch 9': 2, 'Exome Subcohort': 5, 'NP Pilot Study': 1, 'Progressor Pilot Study': 1, 'missing': 39} | chi-square (12 levels; Fisher only defined for 2x2) | 0.565 |
| slx_run_mode | categorical (counts) | {'SLX-10722': 2, 'SLX-10725': 0, 'SLX-10729': 1, 'SLX-12451': 5, 'SLX-12452': 3, 'SLX-12453': 2, 'SLX-12455': 2, 'SLX-12456': 4, 'SLX-13692': 4, 'SLX-13696': 1, 'SLX-16273': 2, 'SLX-16276': 0, 'SLX-16277': 0, 'SLX-16278': 2, 'SLX-16279': 0, 'SLX-16691': 1, 'SLX-16692': 1, 'SLX-16693': 1, 'SLX-16694': 1, 'SLX-16695': 2, 'SLX-16696': 2, 'SLX-16697': 1, 'SLX-16698': 0, 'SLX-16699': 2, 'SLX-16700': 1, 'SLX-16756': 2, 'SLX-16757': 1, 'SLX-16781': 1, 'SLX-16783': 0, 'SLX-17965': 1, 'SLX-17966': 0, 'SLX-17971': 1, 'SLX-17972': 1, 'SLX-17973': 0, 'SLX-17974': 2, 'SLX-17976': 0, 'SLX-17977': 1, 'SLX-17978': 1, 'SLX-17980': 2, 'SLX-9242': 0, 'SLX-9246': 1} | {'SLX-10722': 6, 'SLX-10725': 1, 'SLX-10729': 4, 'SLX-12451': 6, 'SLX-12452': 5, 'SLX-12453': 9, 'SLX-12455': 12, 'SLX-12456': 3, 'SLX-13692': 7, 'SLX-13696': 2, 'SLX-16273': 0, 'SLX-16276': 1, 'SLX-16277': 2, 'SLX-16278': 0, 'SLX-16279': 1, 'SLX-16691': 2, 'SLX-16692': 3, 'SLX-16693': 2, 'SLX-16694': 1, 'SLX-16695': 4, 'SLX-16696': 2, 'SLX-16697': 0, 'SLX-16698': 1, 'SLX-16699': 1, 'SLX-16700': 1, 'SLX-16756': 3, 'SLX-16757': 3, 'SLX-16781': 2, 'SLX-16783': 2, 'SLX-17965': 1, 'SLX-17966': 2, 'SLX-17971': 0, 'SLX-17972': 0, 'SLX-17973': 1, 'SLX-17974': 0, 'SLX-17976': 2, 'SLX-17977': 2, 'SLX-17978': 0, 'SLX-17980': 0, 'SLX-9242': 1, 'SLX-9246': 1} | chi-square (41 levels; Fisher only defined for 2x2) | 0.51 |
| scanner_model_mode | categorical (counts) | {'C13210': 6, 'C13239-01': 48} | {'C13210': 14, 'C13239-01': 82} | Fisher exact | 0.624 |
| scanner_serial_mode | categorical (counts) | {'000023': 6, '000058': 48} | {'000023': 14, '000058': 82} | Fisher exact | 0.624 |
| source_lens_mode | categorical | {'40': 54} | {'40': 96} | constant | None |
| p53_ihc_any_aberrant | categorical (counts) | {'aberrant': 4, 'missing': 31, 'normal': 19} | {'aberrant': 12, 'missing': 44, 'normal': 40} | chi-square (3 levels; Fisher only defined for 2x2) | 0.344 |
| p53_seqsheet_any | categorical (counts) | {'0': 19, '1': 4, 'missing': 31} | {'0': 40, '1': 11, 'missing': 45} | chi-square (3 levels; Fisher only defined for 2x2) | 0.429 |
| grade_source_mode | categorical (counts) | {'master_label_fallback': 4, 'scraped_confirmed': 49, 'scraped_research': 1} | {'master_label_fallback': 36, 'scraped_confirmed': 60, 'scraped_research': 0} | chi-square (3 levels; Fisher only defined for 2x2) | <0.001 |
| next_label_source_mode | categorical (counts) | {'master': 27, 'scrape_exact': 27} | {'master': 57, 'scrape_exact': 39} | Fisher exact | 0.306 |


**C. Arm AUROCs per subgroup (canonical leak-free grade head)**

| subgroup | n | events | img | img_ci | cnv | cnv_ci | head | head_ci | fuse2 | fuse2_ci | fuse3 | fuse3_ci | gain | gain_ci |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 150 | 50 | 0.731 | [0.64, 0.814] | 0.663 | [0.569, 0.754] | 0.753 | [0.659, 0.84] | 0.783 | [0.7, 0.854] | 0.85 | [0.779, 0.909] | 0.067 | [0.022, 0.114] |
| also_in_ERIN | 54 | 14 | 0.704 | [0.55, 0.841] | 0.454 | [0.28, 0.627] | 0.745 | [0.562, 0.899] | 0.58 | [0.395, 0.754] | 0.779 | [0.625, 0.909] | 0.198 | [0.096, 0.317] |
| never_in_ERIN | 96 | 36 | 0.744 | [0.634, 0.85] | 0.76 | [0.652, 0.858] | 0.758 | [0.638, 0.863] | 0.863 | [0.785, 0.932] | 0.885 | [0.816, 0.945] | 0.022 | [-0.027, 0.07] |


**C. CNV-only AUROC within sequencing strata by subgroup**

| stratum | subgroup | n | events | cnv_auroc | cnv_ci |
|---|---|---|---|---|---|
| sequencing sheet (discovery vs validation)=discovery_777 | also_in_ERIN | 25 | 11 | 0.253 | [0.081, 0.487] |
| sequencing sheet (discovery vs validation)=discovery_777 | never_in_ERIN | 57 | 29 | 0.703 | [0.556, 0.835] |
| sequencing sheet (discovery vs validation)=validation_268 | also_in_ERIN | 29 | 3 | 0.538 | [0.143, 0.846] |
| sequencing sheet (discovery vs validation)=validation_268 | never_in_ERIN | 39 | 7 | 0.75 | [0.5, 0.938] |
| SLX run=SLX-10722 | also_in_ERIN | 2 | 1 | nan | None |
| SLX run=SLX-10722 | never_in_ERIN | 6 | 3 | nan | None |
| SLX run=SLX-10725 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-10725 | never_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-10729 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-10729 | never_in_ERIN | 4 | 2 | nan | None |
| SLX run=SLX-12451 | also_in_ERIN | 5 | 2 | nan | None |
| SLX run=SLX-12451 | never_in_ERIN | 6 | 4 | nan | None |
| SLX run=SLX-12452 | also_in_ERIN | 3 | 2 | nan | None |
| SLX run=SLX-12452 | never_in_ERIN | 5 | 4 | nan | None |
| SLX run=SLX-12453 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-12453 | never_in_ERIN | 9 | 2 | nan | None |
| SLX run=SLX-12455 | also_in_ERIN | 2 | 2 | nan | None |
| SLX run=SLX-12455 | never_in_ERIN | 12 | 6 | 0.417 | [0.029, 0.806] |
| SLX run=SLX-12456 | also_in_ERIN | 4 | 0 | nan | None |
| SLX run=SLX-12456 | never_in_ERIN | 3 | 0 | nan | None |
| SLX run=SLX-13692 | also_in_ERIN | 4 | 3 | nan | None |
| SLX run=SLX-13692 | never_in_ERIN | 7 | 6 | nan | None |
| SLX run=SLX-13696 | also_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-13696 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16273 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16273 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16276 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16276 | never_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-16277 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16277 | never_in_ERIN | 2 | 2 | nan | None |
| SLX run=SLX-16278 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16278 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16279 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16279 | never_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-16691 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16691 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16692 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16692 | never_in_ERIN | 3 | 0 | nan | None |
| SLX run=SLX-16693 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16693 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16694 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16694 | never_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16695 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16695 | never_in_ERIN | 4 | 0 | nan | None |
| SLX run=SLX-16696 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16696 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16697 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16697 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16698 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16698 | never_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16699 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16699 | never_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16700 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16700 | never_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16756 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16756 | never_in_ERIN | 3 | 0 | nan | None |
| SLX run=SLX-16757 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16757 | never_in_ERIN | 3 | 0 | nan | None |
| SLX run=SLX-16781 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-16781 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-16783 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-16783 | never_in_ERIN | 2 | 1 | nan | None |
| SLX run=SLX-17965 | also_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-17965 | never_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-17966 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17966 | never_in_ERIN | 2 | 1 | nan | None |
| SLX run=SLX-17971 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-17971 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17972 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-17972 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17973 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17973 | never_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-17974 | also_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-17974 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17976 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17976 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-17977 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-17977 | never_in_ERIN | 2 | 0 | nan | None |
| SLX run=SLX-17978 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-17978 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-17980 | also_in_ERIN | 2 | 2 | nan | None |
| SLX run=SLX-17980 | never_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-9242 | also_in_ERIN | 0 | 0 | nan | None |
| SLX run=SLX-9242 | never_in_ERIN | 1 | 1 | nan | None |
| SLX run=SLX-9246 | also_in_ERIN | 1 | 0 | nan | None |
| SLX run=SLX-9246 | never_in_ERIN | 1 | 0 | nan | None |
| Leanne batch (discovery only)=Batch 1 | also_in_ERIN | 2 | 1 | nan | None |
| Leanne batch (discovery only)=Batch 1 | never_in_ERIN | 6 | 3 | nan | None |
| Leanne batch (discovery only)=Batch 2 | also_in_ERIN | 3 | 2 | nan | None |
| Leanne batch (discovery only)=Batch 2 | never_in_ERIN | 5 | 4 | nan | None |
| Leanne batch (discovery only)=Batch 3 | also_in_ERIN | 5 | 2 | nan | None |
| Leanne batch (discovery only)=Batch 3 | never_in_ERIN | 6 | 4 | nan | None |
| Leanne batch (discovery only)=Batch 4 | also_in_ERIN | 2 | 2 | nan | None |
| Leanne batch (discovery only)=Batch 4 | never_in_ERIN | 12 | 6 | 0.417 | [0.029, 0.806] |
| Leanne batch (discovery only)=Batch 5 | also_in_ERIN | 2 | 0 | nan | None |
| Leanne batch (discovery only)=Batch 5 | never_in_ERIN | 9 | 2 | nan | None |
| Leanne batch (discovery only)=Batch 6 | also_in_ERIN | 4 | 0 | nan | None |
| Leanne batch (discovery only)=Batch 6 | never_in_ERIN | 3 | 0 | nan | None |
| Leanne batch (discovery only)=Batch 8 | also_in_ERIN | 4 | 3 | nan | None |
| Leanne batch (discovery only)=Batch 8 | never_in_ERIN | 7 | 6 | nan | None |
| Leanne batch (discovery only)=Batch 9 | also_in_ERIN | 1 | 1 | nan | None |
| Leanne batch (discovery only)=Batch 9 | never_in_ERIN | 2 | 0 | nan | None |
| Leanne batch (discovery only)=Exome Subcohort | also_in_ERIN | 1 | 0 | nan | None |
| Leanne batch (discovery only)=Exome Subcohort | never_in_ERIN | 5 | 3 | nan | None |
| Leanne batch (discovery only)=NP Pilot Study | also_in_ERIN | 1 | 0 | nan | None |
| Leanne batch (discovery only)=NP Pilot Study | never_in_ERIN | 1 | 0 | nan | None |
| Leanne batch (discovery only)=Progressor Pilot Study | also_in_ERIN | 0 | 0 | nan | None |
| Leanne batch (discovery only)=Progressor Pilot Study | never_in_ERIN | 1 | 1 | nan | None |
| Leanne batch (discovery only)=missing | also_in_ERIN | 29 | 3 | 0.538 | [0.143, 0.846] |
| Leanne batch (discovery only)=missing | never_in_ERIN | 39 | 7 | 0.75 | [0.5, 0.938] |
| read-count tertile=reads_T1_low | also_in_ERIN | 6 | 4 | 0.375 | [0.0, 1.0] |
| read-count tertile=reads_T1_low | never_in_ERIN | 21 | 10 | 0.682 | [0.436, 0.904] |
| read-count tertile=reads_T2 | also_in_ERIN | 8 | 3 | 0.133 | [0.0, 0.571] |
| read-count tertile=reads_T2 | never_in_ERIN | 19 | 8 | 0.682 | [0.393, 0.923] |
| read-count tertile=reads_T3_high | also_in_ERIN | 11 | 4 | 0.25 | [0.0, 0.607] |
| read-count tertile=reads_T3_high | never_in_ERIN | 16 | 10 | 0.817 | [0.545, 1.0] |


**E. Excluding near-baseline progressors**

| exclusion | n | events | head | head_ci | fuse2 | fuse2_ci | fuse3 | fuse3_ci | gain | gain_ci | rows_kept |
|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 150 | 50 | 0.753 | [0.659, 0.84] | 0.783 | [0.7, 0.854] | 0.85 | [0.779, 0.909] | 0.067 | [0.022, 0.114] | nan |
| exclude progressors with event <= 6 m from first row | 144 | 44 | 0.776 | [0.68, 0.861] | 0.794 | [0.715, 0.866] | 0.864 | [0.797, 0.92] | 0.07 | [0.03, 0.113] | nan |
| exclude progressors with event <= 12 m from first row | 142 | 42 | 0.767 | [0.672, 0.856] | 0.791 | [0.711, 0.871] | 0.859 | [0.793, 0.918] | 0.068 | [0.026, 0.112] | nan |
| SECONDARY: drop positive ROWS with DaysToNextBiopsy <= 183 (patient keeps other rows) | 144 | 44 | 0.772 | [0.677, 0.857] | 0.775 | [0.693, 0.85] | 0.856 | [0.786, 0.915] | 0.081 | [0.038, 0.126] | 675.0 |
| SECONDARY: drop positive ROWS with DaysToNextBiopsy <= 365 | 142 | 42 | 0.727 | [0.624, 0.824] | 0.74 | [0.647, 0.829] | 0.801 | [0.717, 0.879] | 0.062 | [0.013, 0.111] | 660.0 |


**F. Grade arms (all 150 patients)**

| arm | n | events | auroc | ci |
|---|---|---|---|---|
| grade_arm | 150 | 50 | 0.682 | [0.585, 0.778] |
| grade_plus_head | 150 | 50 | 0.797 | [0.713, 0.873] |
| grade_maxsofar_arm | 150 | 50 | 0.671 | [0.574, 0.77] |
| grade_maxsofar_plus_head | 150 | 50 | 0.796 | [0.711, 0.872] |
| fuse2_plus_grade | 150 | 50 | 0.843 | [0.776, 0.901] |
| fuse3_plus_grade | 150 | 50 | 0.885 | [0.83, 0.934] |
| head | 150 | 50 | 0.753 | [0.659, 0.84] |
| fuse2 | 150 | 50 | 0.783 | [0.7, 0.854] |
| fuse3 | 150 | 50 | 0.85 | [0.779, 0.909] |
| grade_raw_max | 150 | 50 | 0.687 | [0.601, 0.768] |


**F. Within baseline-NDBE patients**

| definition | n | events | head | head_ci | fuse2 | fuse2_ci | fuse3 | fuse3_ci | img | img_ci | cnv | cnv_ci | gain | gain_ci |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first release row NDBE (Label 0) | 121 | 33 | 0.74 | [0.625, 0.845] | 0.832 | [0.749, 0.904] | 0.881 | [0.815, 0.938] | 0.777 | [0.674, 0.866] | 0.71 | [0.595, 0.816] | 0.049 | [0.009, 0.091] |
| all release rows NDBE | 97 | 21 | 0.724 | [0.573, 0.853] | 0.867 | [0.773, 0.943] | 0.916 | [0.846, 0.969] | 0.781 | [0.654, 0.893] | 0.758 | [0.636, 0.866] | 0.049 | [0.004, 0.101] |


**J. P32 ERIN field AUROCs with 2,000 patient-clustered resamples (source runs used 1,000)**

| run | field | n_cases | n_patients | pos | auroc | ci_2000_patient_clustered |
|---|---|---|---|---|---|---|
| p32b_fields | grade_LGDplus | 2291 | 1613 | 622 | 0.887 | [0.868, 0.905] |
| p32b_fields | im_present | 2224 | 1564 | 1436 | 0.891 | [0.877, 0.904] |
| p32b_fields | inflammation_mod_severe | 1745 | 1292 | 343 | 0.738 | [0.707, 0.77] |
| p32b_fields | squamous_only | 2291 | 1614 | 116 | 0.881 | [0.854, 0.908] |
| p32b_fields | treatment_effect | 2293 | 1614 | 445 | 0.819 | [0.796, 0.843] |
| p32b_fields | ulceration | 2114 | 1505 | 318 | 0.858 | [0.831, 0.883] |
| p32_head_noov | grade_LGDplus | 2247 | 1580 | 620 | 0.89 | [0.872, 0.907] |
| p32_head_noov | inflammation_mod_severe | 1712 | 1269 | 342 | 0.747 | [0.715, 0.778] |
| p32_fields_g0 | grade_HGDplus | 1642 | 1213 | 482 | 0.911 | [0.892, 0.931] |
| p32_fields_g0 | grade_LGDplus | 1642 | 1213 | 644 | 0.861 | [0.839, 0.882] |
| p32_fields_g0 | im_present | 2192 | 1542 | 1406 | 0.897 | [0.884, 0.91] |
| p32_fields_g1 | inflammation_any | 1846 | 1352 | 1517 | 0.607 | [0.57, 0.643] |
| p32_fields_g1 | inflammation_mod_severe | 1846 | 1352 | 373 | 0.742 | [0.709, 0.77] |
| p32_fields_g1 | squamous_only | 2291 | 1614 | 127 | 0.92 | [0.893, 0.944] |
| p32_fields_g1 | ulceration | 2154 | 1527 | 320 | 0.847 | [0.817, 0.875] |
| p32_fields_g2 | gastric_present | 1182 | 958 | 831 | 0.781 | [0.749, 0.812] |
| p32_fields_g2 | p53_abnormal | 473 | 368 | 193 | 0.749 | [0.701, 0.795] |
| p32_fields_g2 | treatment_effect | 2293 | 1614 | 522 | 0.821 | [0.799, 0.842] |
| p32_fields_g3 | certainty_not_definite | 2289 | 1613 | 78 | 0.538 | [0.464, 0.612] |
| p32_fields_g3 | site_goj_or_stomach | 2293 | 1614 | 612 | 0.723 | [0.697, 0.749] |
| p32_fields_g3 | specimen_resection | 2293 | 1614 | 91 | 1.0 | [1.0, 1.0] |


**M. Calibration, Brier and decision-curve net benefit (patient level)**

| arm | n | events | auroc | mean_pred | calib_slope | calib_intercept_at_slope_fit | calib_in_the_large | brier | brier_ci | NB@0.1 | NB@0.15 | NB@0.2 | NB@0.25 | NB@0.3 | NB@0.35 | NB@0.4 | NB@0.45 | NB@0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| image_only_prob | 150 | 50 | 0.731 | 0.549 | 0.616 | -0.992 | -0.888 | 0.245 | [0.206, 0.287] | 0.262 | 0.227 | 0.183 | 0.144 | 0.1 | 0.074 | 0.033 | -0.007 | -0.04 |
| late_mean_prob_release | 150 | 50 | 0.774 | 0.375 | 1.78 | 0.104 | -0.18 | 0.184 | [0.162, 0.207] | 0.26 | 0.22 | 0.197 | 0.156 | 0.135 | 0.119 | 0.109 | 0.098 | 0.053 |
| fuse2_z_plattCV | 150 | 50 | 0.777 | 0.239 | 1.292 | 0.872 | 0.464 | 0.189 | [0.152, 0.225] | 0.271 | 0.242 | 0.19 | 0.124 | 0.135 | 0.111 | 0.104 | 0.077 | 0.053 |
| fuse3_head_z_plattCV | 150 | 50 | 0.845 | 0.246 | 1.72 | 1.338 | 0.428 | 0.168 | [0.132, 0.204] | 0.277 | 0.25 | 0.215 | 0.178 | 0.16 | 0.125 | 0.091 | 0.089 | 0.08 |
| head_prob | 150 | 50 | 0.753 | 0.749 | 1.06 | -2.187 | -1.785 | 0.36 | [0.319, 0.401] | 0.259 | 0.216 | 0.167 | 0.111 | 0.048 | -0.026 | -0.109 | -0.202 | -0.32 |
