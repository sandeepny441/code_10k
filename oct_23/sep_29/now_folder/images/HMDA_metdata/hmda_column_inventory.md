# HMDA metadata: column inventory

This folder lists the columns available in the two HMDA source workbooks used for the lender-ranking work in this project.

| Source workbook | Sheet | Columns |
| --- | --- | ---: |
| hmda-1990-2017.xlsx | beta8 | 62 |
| hmda-2018-present.xlsx | beta3 | 73 |

The schemas are mostly similar, but they are not identical. The 2018-present workbook adds newer HMDA fields such as `LEI`, `EXEMPT18`, closed-end application/origination fields, and `GINNIE`. The older 1990-2017 workbook includes `HMPDYN` and `HUD`, which are not present in the newer workbook.

## Combined column inventory

|   # | Column     | 1990-2017 | 2018-present | Availability      | Description                                                                    |
| --: | ---------- | :-------: | :----------: | ----------------- | ------------------------------------------------------------------------------ |
|   1 | `YEAR`     |    Yes    |     Yes      | Both              | Reporting year.                                                                |
|   2 | `HMPRID`   |    Yes    |     Yes      | Both              | HMDA respondent ID / panel respondent identifier.                              |
|   3 | `HMPDYN`   |    Yes    |              | 1990-2017 only    | Dynamic HMDA respondent identifier used in the older file.                     |
|   4 | `TAXID`    |    Yes    |     Yes      | Both              | Institution tax ID where available.                                            |
|   5 | `CODE`     |    Yes    |     Yes      | Both              | Regulatory agency / source code in the HMDA panel file.                        |
|   6 | `NAMET`    |    Yes    |     Yes      | Both              | Institution name as reported in the transmittal/panel source.                  |
|   7 | `PLACET`   |    Yes    |     Yes      | Both              | Institution city/place as reported in the transmittal/panel source.            |
|   8 | `STATET`   |    Yes    |     Yes      | Both              | Institution state code as reported in the transmittal/panel source.            |
|   9 | `SEQINS`   |    Yes    |     Yes      | Both              | Institution sequence identifier.                                               |
|  10 | `TYPE`     |    Yes    |     Yes      | Both              | Institution type code.                                                         |
|  11 | `RSSD`     |    Yes    |     Yes      | Both              | Federal Reserve RSSD identifier for the institution where available.           |
|  12 | `NAMER`    |    Yes    |     Yes      | Both              | Regulatory institution name.                                                   |
|  13 | `FORER`    |    Yes    |     Yes      | Both              | Regulatory charter/name prefix or form code.                                   |
|  14 | `CHARTR`   |    Yes    |     Yes      | Both              | Charter code.                                                                  |
|  15 | `PLACER`   |    Yes    |     Yes      | Both              | Regulatory city/place.                                                         |
|  16 | `STATER`   |    Yes    |     Yes      | Both              | Regulatory state code.                                                         |
|  17 | `COUNTYR`  |    Yes    |     Yes      | Both              | Regulatory county code.                                                        |
|  18 | `TAXIDR`   |    Yes    |     Yes      | Both              | Regulatory tax ID.                                                             |
|  19 | `RSSDP`    |    Yes    |     Yes      | Both              | Parent RSSD identifier.                                                        |
|  20 | `NAMEP`    |    Yes    |     Yes      | Both              | Parent institution/company name.                                               |
|  21 | `RSSDHH`   |    Yes    |     Yes      | Both              | Highest-holder RSSD identifier.                                                |
|  22 | `NAMEHH`   |    Yes    |     Yes      | Both              | Highest-holder name.                                                           |
|  23 | `ENTITY`   |    Yes    |     Yes      | Both              | Entity identifier used for consolidated lender identity.                       |
|  24 | `NAME`     |    Yes    |     Yes      | Both              | Consolidated institution/lender name.                                          |
|  25 | `FORE`     |    Yes    |     Yes      | Both              | Consolidated charter/name prefix or form code.                                 |
|  26 | `PLACE`    |    Yes    |     Yes      | Both              | Consolidated city/place.                                                       |
|  27 | `STATE`    |    Yes    |     Yes      | Both              | Consolidated state code.                                                       |
|  28 | `COUNTY`   |    Yes    |     Yes      | Both              | Consolidated county code.                                                      |
|  29 | `INSURE`   |    Yes    |     Yes      | Both              | Deposit insurer / insurance code.                                              |
|  30 | `MINBNK`   |    Yes    |     Yes      | Both              | Minority bank indicator.                                                       |
|  31 | `CERT`     |    Yes    |     Yes      | Both              | FDIC certificate number where applicable.                                      |
|  32 | `OCC`      |    Yes    |     Yes      | Both              | OCC identifier or indicator where applicable.                                  |
|  33 | `THRIFT`   |    Yes    |     Yes      | Both              | Thrift identifier or indicator where applicable.                               |
|  34 | `NCUA`     |    Yes    |     Yes      | Both              | NCUA identifier or indicator where applicable.                                 |
|  35 | `ASSETS`   |    Yes    |     Yes      | Both              | Institution assets.                                                            |
|  36 | `ASSETL`   |    Yes    |     Yes      | Both              | Lender or related asset measure used by the panel file.                        |
|  37 | `CRADATE`  |    Yes    |     Yes      | Both              | CRA examination/effective date field.                                          |
|  38 | `CRARATE`  |    Yes    |     Yes      | Both              | CRA rating field.                                                              |
|  39 | `CRAMETH`  |    Yes    |     Yes      | Both              | CRA evaluation method field.                                                   |
|  40 | `FHLB`     |    Yes    |     Yes      | Both              | Federal Home Loan Bank district/code.                                          |
|  41 | `FHLBID`   |    Yes    |     Yes      | Both              | Federal Home Loan Bank identifier.                                             |
|  42 | `HUD`      |    Yes    |              | 1990-2017 only    | HUD identifier/indicator in older schema.                                      |
|  43 | `ORG`      |    Yes    |     Yes      | Both              | Organization identifier for parent/holding-company linkage.                    |
|  44 | `NAMEOR`   |    Yes    |     Yes      | Both              | Organization name.                                                             |
|  45 | `FOREOR`   |    Yes    |     Yes      | Both              | Organization charter/name prefix or form code.                                 |
|  46 | `CHAROR`   |    Yes    |     Yes      | Both              | Organization charter code.                                                     |
|  47 | `ASSORG`   |    Yes    |     Yes      | Both              | Organization assets.                                                           |
|  48 | `REAL14`   |    Yes    |     Yes      | Both              | Real-estate loan or asset-related field from panel source.                     |
|  49 | `LARSNAP`  |    Yes    |     Yes      | Both              | Loan/Application Register snapshot count/indicator.                            |
|  50 | `LAR`      |    Yes    |     Yes      | Both              | Loan/Application Register count.                                               |
|  51 | `PURC`     |    Yes    |     Yes      | Both              | Purchased-loan count.                                                          |
|  52 | `PURCD`    |    Yes    |     Yes      | Both              | Purchased-loan denial/derived count field.                                     |
|  53 | `APPL`     |    Yes    |     Yes      | Both              | Application count.                                                             |
|  54 | `APPLD`    |    Yes    |     Yes      | Both              | Application denial count.                                                      |
|  55 | `APPLM`    |    Yes    |     Yes      | Both              | Applications made/funded-related count field.                                  |
|  56 | `APPLDM`   |    Yes    |     Yes      | Both              | Applications made/funded plus denial-related count field.                      |
|  57 | `ORIG`     |    Yes    |     Yes      | Both              | Originations / loans funded count.                                             |
|  58 | `ORIGD`    |    Yes    |     Yes      | Both              | Origination denial/derived count field.                                        |
|  59 | `ORIGM`    |    Yes    |     Yes      | Both              | Originations made/funded-related count field.                                  |
|  60 | `ORIGDM`   |    Yes    |     Yes      | Both              | Originations made/funded plus denial-related count field.                      |
|  61 | `ENTFUT`   |    Yes    |     Yes      | Both              | Future/successor entity identifier field.                                      |
|  62 | `ORGFUT`   |    Yes    |     Yes      | Both              | Future/successor organization identifier field.                                |
|  63 | `LEI`      |           |     Yes      | 2018-present only | Legal Entity Identifier, used in the newer HMDA schema.                        |
|  64 | `CODE17`   |           |     Yes      | 2018-present only | Legacy 2017-style agency/source code carried into newer file.                  |
|  65 | `EXEMPT18` |           |     Yes      | 2018-present only | 2018 exemption indicator in newer schema.                                      |
|  66 | `LEIR`     |           |     Yes      | 2018-present only | Regulatory LEI where available.                                                |
|  67 | `APPCLO`   |           |     Yes      | 2018-present only | Closed-end application count in newer schema.                                  |
|  68 | `APPCLOD`  |           |     Yes      | 2018-present only | Closed-end application denial count in newer schema.                           |
|  69 | `APPCLOM`  |           |     Yes      | 2018-present only | Closed-end application made/funded-related count in newer schema.              |
|  70 | `APPCLODM` |           |     Yes      | 2018-present only | Closed-end application made/funded plus denial-related count in newer schema.  |
|  71 | `ORICLO`   |           |     Yes      | 2018-present only | Closed-end origination count in newer schema.                                  |
|  72 | `ORICLOD`  |           |     Yes      | 2018-present only | Closed-end origination denial/derived count in newer schema.                   |
|  73 | `ORICLOM`  |           |     Yes      | 2018-present only | Closed-end originations made/funded-related count in newer schema.             |
|  74 | `ORICLODM` |           |     Yes      | 2018-present only | Closed-end originations made/funded plus denial-related count in newer schema. |
|  75 | `GINNIE`   |           |     Yes      | 2018-present only | Ginnie Mae-related count/indicator in newer schema.                            |

## 1990-2017 columns, in source order

| Position | Column |
| ---: | --- |
| 1 | `YEAR` |
| 2 | `HMPRID` |
| 3 | `HMPDYN` |
| 4 | `TAXID` |
| 5 | `CODE` |
| 6 | `NAMET` |
| 7 | `PLACET` |
| 8 | `STATET` |
| 9 | `SEQINS` |
| 10 | `TYPE` |
| 11 | `RSSD` |
| 12 | `NAMER` |
| 13 | `FORER` |
| 14 | `CHARTR` |
| 15 | `PLACER` |
| 16 | `STATER` |
| 17 | `COUNTYR` |
| 18 | `TAXIDR` |
| 19 | `RSSDP` |
| 20 | `NAMEP` |
| 21 | `RSSDHH` |
| 22 | `NAMEHH` |
| 23 | `ENTITY` |
| 24 | `NAME` |
| 25 | `FORE` |
| 26 | `PLACE` |
| 27 | `STATE` |
| 28 | `COUNTY` |
| 29 | `INSURE` |
| 30 | `MINBNK` |
| 31 | `CERT` |
| 32 | `OCC` |
| 33 | `THRIFT` |
| 34 | `NCUA` |
| 35 | `ASSETS` |
| 36 | `ASSETL` |
| 37 | `CRADATE` |
| 38 | `CRARATE` |
| 39 | `CRAMETH` |
| 40 | `FHLB` |
| 41 | `FHLBID` |
| 42 | `HUD` |
| 43 | `ORG` |
| 44 | `NAMEOR` |
| 45 | `FOREOR` |
| 46 | `CHAROR` |
| 47 | `ASSORG` |
| 48 | `REAL14` |
| 49 | `LARSNAP` |
| 50 | `LAR` |
| 51 | `PURC` |
| 52 | `PURCD` |
| 53 | `APPL` |
| 54 | `APPLD` |
| 55 | `APPLM` |
| 56 | `APPLDM` |
| 57 | `ORIG` |
| 58 | `ORIGD` |
| 59 | `ORIGM` |
| 60 | `ORIGDM` |
| 61 | `ENTFUT` |
| 62 | `ORGFUT` |

## 2018-present columns, in source order

| Position | Column     |
| -------: | ---------- |
|        1 | `YEAR`     |
|        2 | `LEI`      |
|        3 | `TAXID`    |
|        4 | `CODE`     |
|        5 | `NAMET`    |
|        6 | `PLACET`   |
|        7 | `STATET`   |
|        8 | `CODE17`   |
|        9 | `HMPRID`   |
|       10 | `SEQINS`   |
|       11 | `EXEMPT18` |
|       12 | `TYPE`     |
|       13 | `RSSD`     |
|       14 | `NAMER`    |
|       15 | `FORER`    |
|       16 | `CHARTR`   |
|       17 | `PLACER`   |
|       18 | `STATER`   |
|       19 | `COUNTYR`  |
|       20 | `TAXIDR`   |
|       21 | `LEIR`     |
|       22 | `RSSDP`    |
|       23 | `NAMEP`    |
|       24 | `RSSDHH`   |
|       25 | `NAMEHH`   |
|       26 | `ENTITY`   |
|       27 | `NAME`     |
|       28 | `FORE`     |
|       29 | `PLACE`    |
|       30 | `STATE`    |
|       31 | `COUNTY`   |
|       32 | `INSURE`   |
|       33 | `MINBNK`   |
|       34 | `CERT`     |
|       35 | `OCC`      |
|       36 | `THRIFT`   |
|       37 | `NCUA`     |
|       38 | `ASSETS`   |
|       39 | `ASSETL`   |
|       40 | `CRADATE`  |
|       41 | `CRARATE`  |
|       42 | `CRAMETH`  |
|       43 | `FHLB`     |
|       44 | `FHLBID`   |
|       45 | `ORG`      |
|       46 | `NAMEOR`   |
|       47 | `FOREOR`   |
|       48 | `CHAROR`   |
|       49 | `ASSORG`   |
|       50 | `REAL14`   |
|       51 | `LAR`      |
|       52 | `LARSNAP`  |
|       53 | `PURC`     |
|       54 | `PURCD`    |
|       55 | `APPL`     |
|       56 | `APPLD`    |
|       57 | `APPLM`    |
|       58 | `APPLDM`   |
|       59 | `ORIG`     |
|       60 | `ORIGD`    |
|       61 | `ORIGM`    |
|       62 | `ORIGDM`   |
|       63 | `APPCLO`   |
|       64 | `APPCLOD`  |
|       65 | `APPCLOM`  |
|       66 | `APPCLODM` |
|       67 | `ORICLO`   |
|       68 | `ORICLOD`  |
|       69 | `ORICLOM`  |
|       70 | `ORICLODM` |
|       71 | `ENTFUT`   |
|       72 | `ORGFUT`   |
|       73 | `GINNIE`   |

## Files in this folder

- `hmda_column_inventory.md`: this readable Markdown inventory.
- `hmda_columns_combined_inventory.csv`: combined sortable column inventory.
- `hmda_columns_1990_2017.csv`: 1990-2017 columns in source order.
- `hmda_columns_2018_present.csv`: 2018-present columns in source order.
