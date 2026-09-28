# Where things stand

Short status of `THE_folder` as of September 26, 2026.

## What's there

`THE_folder` is the HMDA work folder. Almost everything sits in `HMDA_DATA_20_YEARS`:

- Loan files for 2007 through 2025 (`hmda_2007.parquet` … `hmda_2025.parquet`), about 11 GB.
- Institution lookup files (panels, transmittal sheets, name crosswalks).
- A September 16 write-up of 2025 lender concentration and the top 10 profiles.
- A clustering folder with charts, tables, a top-25 archetype pack, and a browser explorer.

## What we did

We used the 2025 file only. Originated loans are HMDA `action_taken = 1`.

- Counted how concentrated originations are. About 6.8 million originations across 4,762 lenders. The top 10 cover about 23% of loans; the top 100 cover about 57%.
- Built one profile row per lender (purpose, product, who bought the loan, geography, borrower and pricing mix). Size was left out of the model so big lenders would not just cluster together.
- Grouped the top 10 into 4 clusters and the top 25 into 5 archetypes (agency-sale nonbanks, portfolio banks and credit unions, builder lenders, VA/government specialists, and broad bank platforms).
- Extended the same idea to the top 30, 40, 50, 70, and 100, and put the results in a standalone HTML explorer.

## What's basically done

The 2025 first pass is finished and saved:

- Concentration note and top-10 profiles.
- Top-10 and top-25 cluster tables, charts, and labels.
- The lender cluster explorer (`September_16th_work_lender_cluster_explorer.html`). Open that file in a browser. It needs no server and no internet. The models are already computed; the page does not refit them.

## Current situation

This is a finished snapshot of 2025, not a multi-year study. The older parquet files are stored and unused by this clustering.

Treat the group names as a reading of the numbers, not a verified business classification. Fit scores are modest, especially for the top 10, and a few groups are very small. “Not sold” means not sold in the reporting year, not that the lender kept the loan forever.

The scripts that built the explorer are not in this folder. What is here is the data and the finished outputs.
