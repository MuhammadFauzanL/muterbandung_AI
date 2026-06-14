import os
import glob
import json
import warnings
import pandas as pd
import numpy as np
import joblib

# Suppress warnings from scikit-learn version mismatch
warnings.filterwarnings("ignore", category=UserWarning)

WORKSPACE_DIR = r"D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace"
CURATED_DIR = os.path.join(WORKSPACE_DIR, "02_Curated")
MODELS_DIR = os.path.join(WORKSPACE_DIR, "07_Models")

# Input files
PRIMARY_DATASET_PATH = os.path.join(CURATED_DIR, "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_PLACES_RATING_COMPLETED_2026-06-13.csv")
MODEL_PATH = os.path.join(MODELS_DIR, "model_sentimen_muterbandung.pkl")

# Accepted review files
ACCEPTED_REVIEW_FILES = [
    "PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-07-37_ACCEPTED_REVIEWS_V2.csv",
    "PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-23_18-30_ACCEPTED_REVIEWS_V2.csv",
    "PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-43_remaining83_ACCEPTED_REVIEWS_V2.csv",
    "PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_19-31_exact79_ACCEPTED_REVIEWS.csv"
]

# Output files
OUT_INFERENCE = os.path.join(CURATED_DIR, "PENGINAPAN_REVIEW_SENTIMENT_INFERENCE_2026-06-14_EXACT_ACCEPTED.csv")
OUT_AGGREGATED = os.path.join(CURATED_DIR, "PENGINAPAN_SENTIMENT_AGGREGATED_2026-06-14_EXACT_ACCEPTED.csv")
OUT_PRIMARY_UPDATED = os.path.join(CURATED_DIR, "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_SENTIMENT_UPDATED_2026-06-14.csv")
OUT_SUMMARY = os.path.join(CURATED_DIR, "penginapan_sentiment_exact_apply_summary_2026-06-14.json")

K_SHRINKAGE = 50.0

def _get_clean_text(row):
    text = str(row['text']).strip() if pd.notna(row['text']) else ""
    translated = str(row['textTranslated']).strip() if 'textTranslated' in row and pd.notna(row['textTranslated']) else ""
    
    if text and text != 'nan':
        return text
    if translated and translated != 'nan':
        return translated
    return ""

def get_sentiment_label(score):
    if score >= 0.6: return "Sangat Positif"
    if score >= 0.2: return "Positif"
    if score >= -0.2: return "Netral"
    if score >= -0.6: return "Negatif"
    return "Sangat Negatif"

def get_confidence_label(count):
    if count >= 30: return "high_review_confidence"
    if count >= 10: return "medium_review_confidence"
    return "low_review_confidence"

def main():
    print("=== PENGINAPAN EXACT REVIEW SENTIMENT APPLY ===")
    
    # 1. Load Primary
    print(f"Loading Primary Dataset: {os.path.basename(PRIMARY_DATASET_PATH)}")
    df_primary = pd.read_csv(PRIMARY_DATASET_PATH, low_memory=False)
    initial_rows = len(df_primary)
    print(f"Primary rows: {initial_rows}")
    
    # 2. Load Reviews
    print("Loading Accepted Reviews...")
    review_dfs = []
    for f_name in ACCEPTED_REVIEW_FILES:
        f_path = os.path.join(CURATED_DIR, f_name)
        if os.path.exists(f_path):
            review_dfs.append(pd.read_csv(f_path, low_memory=False))
        else:
            print(f"  [WARN] File not found: {f_name}")
            
    df_reviews = pd.concat(review_dfs, ignore_index=True)
    print(f"Total accepted review rows raw: {len(df_reviews)}")
    
    # 3. Clean and Deduplicate Reviews
    df_reviews['cleaned_text'] = df_reviews.apply(_get_clean_text, axis=1)
    df_reviews = df_reviews[df_reviews['cleaned_text'] != ""]
    print(f"Reviews with text: {len(df_reviews)}")
    
    df_reviews = df_reviews.drop_duplicates(subset=['target_penginapan_id', 'reviewId', 'cleaned_text'])
    print(f"Reviews after deduplication: {len(df_reviews)}")
    
    if len(df_reviews) == 0:
        print("No text reviews to process. Exiting.")
        return
        
    # 4. Load Model
    print("Loading NLP Sentiment Model...")
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return
        
    classes = list(model.classes_)
    pos_idx = classes.index("Positif") if "Positif" in classes else -1
    neg_idx = classes.index("Negatif") if "Negatif" in classes else -1
    neu_idx = classes.index("Netral") if "Netral" in classes else -1
    
    print("Predicting sentiment...")
    texts = df_reviews['cleaned_text'].tolist()
    probas = model.predict_proba(texts)
    preds = model.predict(texts)
    
    scores = []
    confidence_means = []
    for p in probas:
        pos_val = p[pos_idx] if pos_idx >= 0 else 0.0
        neg_val = p[neg_idx] if neg_idx >= 0 else 0.0
        scores.append(pos_val - neg_val)
        confidence_means.append(max(p))
        
    df_reviews['sentiment_prediction'] = preds
    df_reviews['proba_positif'] = probas[:, pos_idx] if pos_idx >= 0 else 0.0
    df_reviews['proba_negatif'] = probas[:, neg_idx] if neg_idx >= 0 else 0.0
    df_reviews['proba_netral'] = probas[:, neu_idx] if neu_idx >= 0 else 0.0
    df_reviews['review_sentiment_score'] = scores
    df_reviews['review_confidence'] = confidence_means
    
    # Export inference
    df_reviews.to_csv(OUT_INFERENCE, index=False)
    print(f"Saved inference results to {os.path.basename(OUT_INFERENCE)}")
    
    # 5. Aggregate per Target
    print("Aggregating sentiment per penginapan...")
    global_mean_score = np.mean(scores)
    
    agg_funcs = {
        'reviewId': 'count',
        'review_sentiment_score': 'mean',
        'review_confidence': 'mean',
        'proba_positif': 'mean',
        'proba_negatif': 'mean',
        'proba_netral': 'mean'
    }
    df_agg = df_reviews.groupby('target_penginapan_id').agg(agg_funcs).reset_index()
    df_agg.rename(columns={
        'reviewId': 'hotel_review_count_analyzed',
        'review_sentiment_score': 'hotel_sentiment_score',
        'review_confidence': 'hotel_sentiment_confidence_mean'
    }, inplace=True)
    
    # Count sentiments
    sentiment_counts = df_reviews.groupby(['target_penginapan_id', 'sentiment_prediction']).size().unstack(fill_value=0)
    for col in ['Positif', 'Negatif', 'Netral']:
        if col not in sentiment_counts.columns:
            sentiment_counts[col] = 0
            
    sentiment_counts.rename(columns={'Positif': 'positive_review_count', 'Negatif': 'negative_review_count', 'Netral': 'neutral_review_count'}, inplace=True)
    df_agg = df_agg.merge(sentiment_counts, left_on='target_penginapan_id', right_index=True, how='left')
    
    # Bayesian Shrinkage
    df_agg['hotel_adjusted_sentiment_score'] = (
        (df_agg['hotel_review_count_analyzed'] * df_agg['hotel_sentiment_score'] + K_SHRINKAGE * global_mean_score) 
        / (df_agg['hotel_review_count_analyzed'] + K_SHRINKAGE)
    )
    
    df_agg['hotel_sentiment_label'] = df_agg['hotel_sentiment_score'].apply(get_sentiment_label)
    df_agg['hotel_adjusted_sentiment_label'] = df_agg['hotel_adjusted_sentiment_score'].apply(get_sentiment_label)
    df_agg['hotel_review_confidence_label'] = df_agg['hotel_review_count_analyzed'].apply(get_confidence_label)
    df_agg['hotel_sentiment_model_source'] = "tfidf_svm_penginapan_exact_v1"
    
    # Save Aggregated
    df_agg.to_csv(OUT_AGGREGATED, index=False)
    print(f"Saved aggregated results to {os.path.basename(OUT_AGGREGATED)} (Targets: {len(df_agg)})")
    
    # 6. Merge to Primary Dataset
    print("Merging to Primary Dataset...")
    # Clean old sentiment columns if exist to prevent suffix collisions, except we might want to keep the old ones.
    # Actually, the requirement is to update sentiment. Let's merge and update.
    
    merge_cols = df_agg.columns.tolist()
    merge_cols.remove('target_penginapan_id')
    
    df_merged = df_primary.merge(
        df_agg, 
        left_on='penginapan_id', 
        right_on='target_penginapan_id', 
        how='left',
        suffixes=('_old', '')
    )
    
    # For properties that had an old sentiment but no new review, we should ideally keep the old sentiment.
    # If the document states we just update the ones with new reviews, we coalesce.
    if 'hotel_adjusted_sentiment_score_old' in df_merged.columns:
        for c in merge_cols:
            if f'{c}_old' in df_merged.columns:
                df_merged[c] = df_merged[c].fillna(df_merged[f'{c}_old'])
                df_merged.drop(columns=[f'{c}_old'], inplace=True)
                
    # Fallback for empty
    mask_empty = df_merged['hotel_adjusted_sentiment_score'].isna()
    df_merged.loc[mask_empty, 'sentiment_available'] = False
    df_merged.loc[mask_empty, 'hotel_sentiment_model_source'] = 'unavailable'
    df_merged.loc[mask_empty, 'hotel_sentiment_fallback_reason'] = 'no_accepted_text_review'
    df_merged.loc[~mask_empty, 'sentiment_available'] = True
    
    # Update completion priority if sentiment is now filled
    if 'completion_priority_data_focus' in df_merged.columns:
        mask_filled = (~df_merged['hotel_adjusted_sentiment_score'].isna()) & (df_merged['completion_priority_data_focus'] == 'P2_Sentiment_Missing')
        df_merged.loc[mask_filled, 'completion_priority_data_focus'] = 'Completed_Or_Low_Priority'
        
    print(f"Merged rows: {len(df_merged)}")
    
    # Assertions
    assert len(df_merged) == initial_rows, f"Row count changed! {initial_rows} -> {len(df_merged)}"
    assert df_merged['latitude'].isna().sum() == 0, "Latitude lost!"
    assert df_merged['longitude'].isna().sum() == 0, "Longitude lost!"
    
    # Check coverage
    coverage_before = df_primary['hotel_adjusted_sentiment_score'].notna().sum() if 'hotel_adjusted_sentiment_score' in df_primary.columns else 0
    coverage_after = df_merged['hotel_adjusted_sentiment_score'].notna().sum()
    print(f"Sentiment coverage: {coverage_before} -> {coverage_after} properties")
    
    df_merged.to_csv(OUT_PRIMARY_UPDATED, index=False)
    print(f"Saved updated primary dataset to {os.path.basename(OUT_PRIMARY_UPDATED)}")
    
    summary = {
        "timestamp": "2026-06-14",
        "primary_rows_initial": initial_rows,
        "primary_rows_final": len(df_merged),
        "total_reviews_processed": len(df_reviews),
        "target_properties_analyzed": len(df_agg),
        "sentiment_coverage_before": int(coverage_before),
        "sentiment_coverage_after": int(coverage_after),
        "global_mean_score_used_for_shrinkage": float(global_mean_score),
        "bayesian_k_shrinkage": K_SHRINKAGE
    }
    
    with open(OUT_SUMMARY, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary to {os.path.basename(OUT_SUMMARY)}")
    print("DONE.")

if __name__ == "__main__":
    main()
