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
    zu_grob = ['Unknown', 'General', haupt_domain] 
    
    df_domain = df[df['Domain'] == haupt_domain]
    bekannte_fields = df_domain[~df_domain['Field'].isin(zu_grob)]['Field']
    
    if bekannte_fields.empty:
        top_fields = []
    else:
        top_fields = bekannte_fields.value_counts().head(3).index.tolist()
    print(f"🔬 Thematischer Kern (Top 3 Fields): {top_fields}")
    
    # --- 3. DIE VIP-WHITELIST (Die sicheren Häfen) ---
    df_safe = df[df['Field'].isin(top_fields)].copy()
    uni_counts = df_safe['Uni'].value_counts()
    sichere_unis = set(uni_counts[uni_counts >= 2].index)
    
    # --- NEU: 3.5 DIE BLACKLIST (Das Immunsystem) ---
    # Finde alle Felder, die nichts mit den Top-Feldern oder den groben Feldern zu tun haben
    fremde_felder_df = df[~df['Field'].isin(top_fields + zu_grob)]
    
    # Unis, die in diesen fremden Feldern publizieren, sind verdächtig
    verdächtige_unis = set(fremde_felder_df['Uni'].unique())
    
    # Eine Uni ist nur ECHT böse, wenn sie uns nicht schon als VIP-Uni bekannt ist (wie die LMU)
    echte_boese_unis = verdächtige_unis - sichere_unis
    
    # --- 4. DER GERICHTS-FILTER ---
    # Bedingung A: Ist ein hartes Kern-Paper (Top 3 Field)
    bedingung_kern = df['Field'].isin(top_fields)
    
    # Bedingung B: Rettung durch VIP-Uni in erlaubten Domänen
    erlaubte_domains = [haupt_domain, 'Unknown']
    bedingung_rettung = (~bedingung_kern) & (df['Uni'].isin(sichere_unis)) & (df['Domain'].isin(erlaubte_domains))
    
    # NEU: Der finale Scharfrichter -> Das Paper darf NICHT von einer bösen Uni kommen!
    bedingung_nicht_boese = ~df['Uni'].isin(echte_boese_unis)
    
    # Anwenden: (Kern ODER Rettung) UND NICHT Böse
    df_clean = df[(bedingung_kern | bedingung_rettung) & bedingung_nicht_boese].copy()
    
    # Logge das Schlachtfest
    geloeschte = df[~df.index.isin(df_clean.index)]
    for _, row in geloeschte.iterrows():
        print(f"🗑️ Blockiert ({row['Field'][:20]}... | {row['Uni'][:20]}...): '{row['Titel'][:40]}...'")

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