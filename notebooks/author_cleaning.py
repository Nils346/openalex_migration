import pandas as pd

def remove_ghost_papers(df):
    if df.empty: return df
        
    print("\n--- 👻 GHOST AUTHOR SCAN ---")
    
    # --- 1. DIE MAKRO-EBENE (Domain) ---
    bekannte_domains = df[df['Domain'] != 'Unknown']['Domain']
    if bekannte_domains.empty: return df
    haupt_domain = bekannte_domains.value_counts().index[0]
    print(f"🌍 Makro-Domäne gesichert: '{haupt_domain}'")
    
    # --- 2. DIE MIKRO-EBENE (Spezifische Fields) ---
    # DYNAMISCH FÜR ALLE FÄCHER (MINT etc.):
    # Das generische Field heißt bei OpenAlex oft exakt wie die Domain!
    zu_grob = ['Unknown', 'General', haupt_domain] 
    
    df_domain = df[df['Domain'] == haupt_domain]
    bekannte_fields = df_domain[~df_domain['Field'].isin(zu_grob)]['Field']
    
    if bekannte_fields.empty:
        top_fields = []
    else:
        # Wir nehmen die Top 3 (statt 2), um False Negatives zu vermeiden
        top_fields = bekannte_fields.value_counts().head(3).index.tolist()
    print(f"🔬 Thematischer Kern (Top 3 Fields): {top_fields}")
    
    # --- 3. DIE VIP-WHITELIST BAUEN ---
    # Unis, an denen mind. 2 echte Kern-Papiere geschrieben wurden
    df_safe = df[df['Field'].isin(top_fields)].copy()
    uni_counts = df_safe['Uni'].value_counts()
    sichere_unis = set(uni_counts[uni_counts >= 2].index)
    
    # --- 4. DER GERICHTS-FILTER (Generalisiert) ---
    # Bedingung A: Ist ein hartes Kern-Paper (Top 3 Field)
    bedingung_kern = df['Field'].isin(top_fields)
    
    # Bedingung B: Paper hat ein anderes/generisches Feld ODER ist interdisziplinär, 
    # ABER es wurde an einer unserer 100% sicheren VIP-Unis geschrieben! (Rettet Ausreißer)
    bedingung_rettung = (~bedingung_kern) & (df['Uni'].isin(sichere_unis))
    
    df_clean = df[bedingung_kern | bedingung_rettung].copy()
    
    # Logge das Schlachtfest
    geloeschte = df[~df.index.isin(df_clean.index)]
    for _, row in geloeschte.iterrows():
        print(f"🗑️ Blockiert ({row['Field']} | {row['Uni'][:20]}...): '{row['Titel'][:40]}...'")

    # --- 5. DAS BIOLOGISCHE FENSTER ---
    if not df_clean.empty:
        median_jahr = df_clean['Jahr'].median()
        min_jahr = median_jahr - 35
        max_jahr = median_jahr + 35
        
        geister_zeit_df = df_clean[(df_clean['Jahr'] < min_jahr) | (df_clean['Jahr'] > max_jahr)]
        if not geister_zeit_df.empty:
            print(f"⏳ Biologisches Fenster: {int(min_jahr)} bis {int(max_jahr)}")
            for _, row in geister_zeit_df.iterrows():
                print(f"🗑️ Falsche Zeit ({row['Jahr']}): '{row['Titel'][:40]}...'")
                
        df_clean = df_clean[(df_clean['Jahr'] >= min_jahr) & (df_clean['Jahr'] <= max_jahr)].copy()
    
    print("----------------------------\n")
    return df_clean.sort_values(by=['Jahr', 'Datum']).reset_index(drop=True)