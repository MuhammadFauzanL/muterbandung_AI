import os
import sys
import pandas as pd
import numpy as np

# Adjust the path to import penginapan_recommender
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from penginapan_recommender import PenginapanRecommender

GROUNDTRUTH_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Penginapan_Workspace",
    "02_Curated",
    "penginapan_groundtruth_queries.csv"
)

def evaluate():
    print(f"[INFO] Loading Ground Truth from: {GROUNDTRUTH_PATH}")
    if not os.path.exists(GROUNDTRUTH_PATH):
        print(f"[ERROR] File not found: {GROUNDTRUTH_PATH}")
        sys.exit(1)
        
    gt_df = pd.read_csv(GROUNDTRUTH_PATH)
    print("[INFO] Initializing Penginapan Recommender...")
    
    try:
        recommender = PenginapanRecommender()
    except Exception as e:
        print(f"[ERROR] Failed to initialize recommender: {e}")
        sys.exit(1)
        
    metrics = []
    
    print("\n" + "="*50)
    print("[STARTING EVALUATION] Precision@5 & NDCG@5")
    print("="*50)
    
    for idx, row in gt_df.iterrows():
        query = str(row['query']) if pd.notna(row['query']) else ""
        expected_types = str(row['expected_property_type']).lower().split('|') if pd.notna(row['expected_property_type']) else []
        forbidden_types = str(row['forbidden_property_type']).lower().split('|') if pd.notna(row['forbidden_property_type']) else []
        
        expected_types = [t.strip() for t in expected_types if t.strip()]
        forbidden_types = [t.strip() for t in forbidden_types if t.strip()]
        
        user_lat = float(row['user_lat']) if pd.notna(row['user_lat']) else None
        user_lon = float(row['user_lon']) if pd.notna(row['user_lon']) else None
        
        res = recommender.recommend(query=query, user_lat=user_lat, user_lon=user_lon, top_k=5)
        recs = res.get("recommendations", [])
        
        if not recs:
            metrics.append({"id": row['id'], "query": query, "p5": 0.0, "ndcg5": 0.0})
            print(f"[{row['id']}] '{query}' -> NO RESULTS")
            continue
            
        relevance_scores = []
        top_types = []
        for rec in recs:
            p_type = str(rec.get('property_type')).lower()
            top_types.append(p_type)
            rel = 1  # Default relevance is 1 if it's not forbidden
            
            if p_type in forbidden_types:
                rel = 0
            elif expected_types:
                if p_type in expected_types:
                    rel = 1
                else:
                    rel = 0
                    
            relevance_scores.append(rel)
            
        p5 = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        dcg5 = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(relevance_scores))
        
        ideal_relevance = sorted(relevance_scores, reverse=True)
        idcg5 = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(ideal_relevance))
        
        ndcg5 = dcg5 / idcg5 if idcg5 > 0 else (0.0 if dcg5 == 0 and ideal_relevance and ideal_relevance[0] > 0 else 1.0)
        
        metrics.append({
            "id": row['id'], 
            "query": query, 
            "p5": p5, 
            "ndcg5": ndcg5, 
            "top_types": top_types
        })
        
        print(f"[{row['id']}] '{query}'")
        print(f"   => Expected: {expected_types} | Forbidden: {forbidden_types}")
        print(f"   => Top 5 types : {top_types}")
        print(f"   => Relevance   : {relevance_scores}")
        print(f"   => P@5: {p5:.2f} | NDCG@5: {ndcg5:.2f}")
        print("-" * 50)

    
    avg_p5 = np.mean([m['p5'] for m in metrics])
    avg_ndcg5 = np.mean([m['ndcg5'] for m in metrics])
    
    print("\n" + "="*50)
    print("[EVALUATION SUMMARY]")
    print("="*50)
    print(f"Total Queries Evaluated : {len(metrics)}")
    print(f"Average Precision@5     : {avg_p5:.4f}")
    print(f"Average NDCG@5          : {avg_ndcg5:.4f}")
    
    # Save report
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "PENGINAPAN_EVALUATION_REPORT.md")
    with open(report_path, "w") as f:
        f.write(f"# Penginapan Recommender Evaluation Report\n\n")
        f.write(f"**Total Queries Evaluated:** {len(metrics)}\n")
        f.write(f"**Average Precision@5:** {avg_p5:.4f}\n")
        f.write(f"**Average NDCG@5:** {avg_ndcg5:.4f}\n\n")
        f.write("## Detailed Results\n")
        f.write("| ID | Query | P@5 | NDCG@5 | Top Property Types |\n")
        f.write("|---|---|---|---|---|\n")
        for m in metrics:
            types_str = ", ".join(m['top_types'])
            f.write(f"| {m['id']} | {m['query']} | {m['p5']:.2f} | {m['ndcg5']:.2f} | {types_str} |\n")
            
    print(f"\n[INFO] Report saved to: {report_path}")

if __name__ == "__main__":
    evaluate()
