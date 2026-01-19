import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('raw_pools/ELP_wordlist.csv')

# Clean the data first
# Convert SUBTLWF - remove commas and convert to numeric
df['SUBTLWF_clean'] = df['SUBTLWF'].astype(str).str.replace(',', '').str.replace('#', '')
df['SUBTLWF_numeric'] = pd.to_numeric(df['SUBTLWF_clean'], errors='coerce')

# Convert NSyll - replace "#" with NaN and convert to numeric
df['NSyll_numeric'] = pd.to_numeric(df['NSyll'].replace('#', np.nan), errors='coerce')

# Convert NMorph - replace "#" with NaN and convert to numeric
df['NMorph_numeric'] = pd.to_numeric(df['NMorph'].replace('#', np.nan), errors='coerce')

# Filter by basic criteria
# 1. Length between 3 and 9
df_filtered = df[(df['Length'] >= 3) & (df['Length'] <= 9)]

# 2. NSyll == 2
df_filtered = df_filtered[df_filtered['NSyll_numeric'] == 2]

# 3. POS == "NN" (some entries have multiple POS like "VB|NN", so we check if "NN" is in the string)
# Also exclude entries where POS is "#"
df_filtered = df_filtered[df_filtered['POS'].fillna('').str.contains('NN') & (df_filtered['POS'] != '#')]

# 4. Remove rows where SUBTLWF is missing or non-numeric
df_filtered = df_filtered[df_filtered['SUBTLWF_numeric'].notna()]

# 5. Remove plurals - look for the plural marker ">s>" in MorphSp field
# This is more precise than NMorph, as it only targets actual plurals
df_filtered = df_filtered[~df_filtered['MorphSp'].fillna('').str.contains('>s>')]

# 6. Remove proper nouns - filter out words that start with a capital letter
df_filtered = df_filtered[~df_filtered['Word'].str[0].str.isupper()]

# Calculate the 25th and 75th percentiles for SUBTLWF (middle 50%)
lower_percentile = df_filtered['SUBTLWF_numeric'].quantile(0.25)
upper_percentile = df_filtered['SUBTLWF_numeric'].quantile(0.75)

# Filter by middle 50% of SUBTLWF values
df_filtered = df_filtered[
    (df_filtered['SUBTLWF_numeric'] >= lower_percentile) &
    (df_filtered['SUBTLWF_numeric'] <= upper_percentile)
]

# Extract words and save to file
words = df_filtered['Word'].tolist()

# Save to text file, one word per line
with open('raw_pools/filtered_words.txt', 'w') as f:
    for word in words:
        f.write(f"{word}\n")

print(f"Filtered {len(words)} words")
print(f"SUBTLWF range: {lower_percentile:.2f} to {upper_percentile:.2f}")
print(f"Words saved to raw_pools/filtered_words.txt")
