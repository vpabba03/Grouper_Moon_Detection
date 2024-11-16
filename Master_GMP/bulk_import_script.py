import pandas as pd
import numpy as np
import argparse

def extract_boxes_script(year):
    # Read CSV files
    all_boxes = pd.read_csv("Master_GMP.csv", low_memory=False)
    boxes_uploaded = pd.read_csv("collection_of_uploaded_bboxes_full.csv")
    
    # Find non-matching boxes
    non_matching_in_all_boxes = all_boxes[~all_boxes['ImageID'].isin(boxes_uploaded['mediaAsset'])]
    year_boxes = non_matching_in_all_boxes[non_matching_in_all_boxes['Year'] == year].sort_values(by=['Month', 'Day'])
    
    year_boxes.rename(columns = {'Unnamed: 0':'Index'}, inplace=True)
    year_boxes.set_index('Index', inplace=True)
    
    # Filter for non-zero Month or Day and take first 200
    year_boxes = year_boxes[(year_boxes['Month'] != 0) | (year_boxes['Day'] != 0)].sort_index()
    boxes_part_1 = year_boxes.head(200)
    print_boxes = boxes_part_1['ImageID'].to_list()
    
    # Write to file with dynamic year in filename
    with open(f"{year}_files.txt", "w") as outfile:
        outfile.write("','".join(print_boxes))
    
    # Select required columns
    boxes_df = boxes_part_1[[
        'IndexID', 'Encounter.occurrenceID', 'Imported Image ID', 'Year', 'Month', 
        'Day', 'Hour', 'Minutes', 'DecimalLatitude', 'DecimalLongitude', 
        'LocationDescription', 'Country', 'LocationID', 'Genus', 'Species', 
        'IndividualIDGrouperSpotter', 'IndividualNickname', 'Sex', 'VideoComments', 
        'ImageComments', 'Encounter.submitter.emailAddress', 'PhotographerFullName', 
        'PhotographerEmail', 'Fish_Length', 'Distinguishing Features', 'LivingStatus', 
        'Lifestage', 'FishDepth', 'Behavior', 'TissueSampleID', 
        'Encounter.mediaAsset0.keywords', 'Encounter.mediaAsset1.keywords'
    ]]
    
    # Handle multiple images per IndexID
    seen = {}
    media_asset_columns = []
    
    # First pass: determine maximum number of media assets needed
    max_assets = boxes_df.groupby('IndexID').size().max()
    
    # # Create necessary mediaAsset columns
    # for i in range(max_assets):
    #     column_name = f"mediaAsset{i}"
    #     boxes_df.loc[:, column_name] = None
    #     media_asset_columns.append(column_name)
    
    # # Second pass: populate mediaAsset columns
    # for index, row in boxes_df.iterrows():
    #     indexID = row["IndexID"]
    #     imported_image_id = row["Imported Image ID"]
        
    #     if indexID in seen:
    #         seen[indexID]['count'] += 1
    #         column_name = f"mediaAsset{seen[indexID]['count']}"
    #         boxes_df.loc[index, column_name] = imported_image_id
    #     else:
    #         seen[indexID] = {'count': 0}
    #         boxes_df.loc[index, 'mediaAsset0'] = imported_image_id
    
    # Create necessary mediaAsset columns
    for i in range(max_assets):
        column_name = f"mediaAsset{i}"
        boxes_df.loc[:, column_name] = None
        media_asset_columns.append(column_name)
    
    # Create a dictionary to store the first index for each IndexID
    first_instances = {}
    for index, row in boxes_df.iterrows():
        indexID = row["IndexID"]
        if indexID not in first_instances:
            first_instances[indexID] = index
    
    # Second pass: populate mediaAsset columns
    for index, row in boxes_df.iterrows():
        indexID = row["IndexID"]
        imported_image_id = row["Imported Image ID"]
        
        if indexID in seen:
            seen[indexID]['count'] += 1
            column_name = f"mediaAsset{seen[indexID]['count']}"
            # Use the first instance's index instead of current row's index
            first_index = first_instances[indexID]
            boxes_df.loc[first_index, column_name] = imported_image_id
        else:
            seen[indexID] = {'count': 0}
            first_index = first_instances[indexID]
            boxes_df.loc[first_index, 'mediaAsset0'] = imported_image_id
    print(seen)
    
    # Drop original columns and add required new columns
    boxes_df.drop(columns=['IndexID', 'Imported Image ID'], inplace=True, errors='ignore')
    
    # Define new column names
    new_column_names = [
        "Encounter.occurrenceID", "Encounter.mediaAsset0", "Encounter.mediaAsset1", 
        "Encounter.year", "Encounter.month", "Encounter.day", "Encounter.hour", 
        "Encounter.minutes", "Encounter.decimalLongitude", "Encounter.decimalLatitude", 
        "Encounter.verbatimLocality", "Encounter.country", "Encounter.locationID", 
        "Encounter.genus", "Encounter.specificEpithet", "MarkedIndividual.individualID", 
        "MarkedIndividual.nickname", "Encounter.sex", "Occurrence.comments", 
        "Encounter.occurrenceRemarks", "Encounter.submitter0.emailAddress", 
        "Encounter.state", "Encounter.photographer0.fullName", 
        "Encounter.photographer0.emailAddress", "Encounter.measurement0", 
        "Encounter.measurement1", "Encounter.distinguishingScar", 
        "Encounter.livingStatus", "Encounter.lifeStage", "Encounter.depth", 
        "Encounter.behavior", "TissueSample.sampleID", "Encounter.mediaAsset0.keywords", 
        "Encounter.mediaAsset1.keywords"
    ]

    # Add required empty columns (if not already present)
    if 'Encounter.mediaAsset1' not in boxes_df.columns:
        boxes_df.insert(2, "Encounter.mediaAsset1", np.nan)
    if 'Encounter.state' not in boxes_df.columns:
        boxes_df.insert(21, "Encounter.state", np.nan)
    if 'Encounter.measurement2' not in boxes_df.columns:
        boxes_df.insert(25, "Encounter.measurement2", np.nan)

    # Check for column count match before renaming
    if len(boxes_df.columns) == len(new_column_names):
        # Rename columns if the count matches
        boxes_df.columns = new_column_names
    else:
        print(f"Error: Length mismatch between DataFrame columns ({len(boxes_df.columns)}) "
              f"and new_column_names ({len(new_column_names)})")
    
    # Save to CSV
    boxes_df.to_csv(f'{year}_Bulk_Import_10_23_2024.csv', index=False)
    
    return boxes_df

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Process box data for a specific year.')
    
    # Add arguments
    parser.add_argument('year', type=int, help='Year to process (e.g., 2015)')
    parser.add_argument('--master', type=str, default="Master_GMP.csv",
                      help='Path to Master_GMP.csv (default: Master_GMP.csv)')
    parser.add_argument('--uploaded', type=str, default="collection_of_uploaded_bboxes_full.csv",
                      help='Path to uploaded boxes CSV (default: collection_of_uploaded_bboxes_full.csv)')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Execute the main function
        df = extract_boxes_script(args.year)
        print(f"Successfully processed data for year {args.year}")
        print(f"Output saved to {args.year}_Bulk_Import_10_23_2024.csv")
    except Exception as e:
        print(f"Error processing data: {str(e)}")

if __name__ == "__main__":
    main()