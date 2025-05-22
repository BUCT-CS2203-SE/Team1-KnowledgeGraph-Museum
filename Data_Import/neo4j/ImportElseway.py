from neo4j import GraphDatabase
import pandas as pd
import re

# 加载 CSV
df = pd.read_csv("../Process_ALL/datasets/Process_translate_ds.csv")

# Neo4j 连接
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))


def split_multi_values(value):
    if pd.isna(value):
        return []
    return [v.strip() for v in re.split(r'[；;，,、/]', str(value)) if v.strip()]


with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    for _, row in df.iterrows():
        art_id = str(row["id"])
        Title = row.get("Title", '')
        Artist = row.get("Artist", '')

        # 创建 Artifact 节点（用 id 作为唯一键）
        # 创建 Artifact 节点（用 id 作为唯一键）
        session.run("""
            MERGE (a:Artifact {id: $id})
            SET a.Title = $Title,
                a.Artist = $Artist,
                a.Dynasty = $Dynasty,
                a.CreditLine = $CreditLine,
                a.Dimensions = $Dimensions,
                a.Materials = $Materials,
                a.Description = $Description,
                a.Inscribed = $Inscribed
        """, id=art_id, Title=row.get("Title", ""),
                    Artist=row.get("Artist", ""),
                    Dynasty=row.get("Dynasty", ""),
                    CreditLine=row.get("CreditLine", ""),
                    Dimensions=row.get("Dimensions", ""),
                    Materials=row.get("Materials", ""),
                    Description=row.get("Description", ""),
                    Inscribed=row.get("Inscribed", ""))

        # 处理 Museum
        museum = row.get("Museum")
        if pd.notna(museum):
            session.run("""
                MERGE (m:Museum {name: $museum})
                WITH m
                MATCH (a:Artifact {id: $id})
                MERGE (a)-[:KEPT_BY]->(m)
            """, id=art_id, museum=museum.strip())

        # 处理 PlaceOri
        place = row.get("PlaceOri")
        if pd.notna(place):
            session.run("""
                MERGE (p:PlaceOri {name: $place})
                WITH p
                MATCH (a:Artifact {id: $id})
                MERGE (a)-[:ORIGINATED_FROM]->(p)
            """, id=art_id, place=place.strip())

        # 处理 Classifications
        classifications = row.get("Classifications")
        if pd.notna(classifications):
            session.run("""
                        MERGE (c:Classification {name: $cls})
                        WITH c
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:HAS_CLASSIFICATION]->(c)
                    """, id=art_id, cls=classifications.strip())

        for period in split_multi_values(row.get('periods')):
            session.run("""
                        MERGE (p:Period {name: $period})
                        MERGE (a:Artifact {id: $id})
                        MERGE (a)-[:HAS_PERIOD]->(p)
                    """, id=art_id, period=period)

        mediums = row.get("Medium")
        if pd.notna(mediums):
            for med in split_multi_values(mediums):
                if med:
                    session.run("""
                        MERGE (m:Medium {name: $medium})
                        WITH m
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:USES_MEDIUM]->(m)
                    """, id=art_id, medium=med)

        # 处理 Dynasty
        dynasty = row.get("Dynasty")
        if pd.notna(dynasty):
            for dynastyonly in split_multi_values(dynasty):
                if dynastyonly:
                    session.run("""
                        MERGE (d:Dynasty {name: $dynasty})
                        WITH d
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:BELONGS_TO_DYNASTY]->(d)
                    """, id=art_id, dynasty=dynastyonly.strip())

        materials = row.get("Materials")
        if pd.notna(materials):
            for material in split_multi_values(materials):
                if materials:
                    session.run("""
                            MERGE (p:Material {name: $material})
                            WITH p
                            MATCH (a:Artifact {id: $id})
                            MERGE (a)-[:原料是]->(p)
                        """, id=art_id, material=material)

        print(row.get('id'))
