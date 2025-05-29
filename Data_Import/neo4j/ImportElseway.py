from neo4j import GraphDatabase
import pandas as pd
import re

# 加载 CSV
df = pd.read_csv("../Process_ALL/datasets/Process_end2.csv")

# Neo4j 连接
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Cs22032025"))


def split_multi_values(value):
    if pd.isna(value):
        return []
    return [v.strip() for v in re.split(r'[；;，,、/]', str(value)) if v.strip()]


with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    for _, row in df.iterrows():
        art_id = str(row["id"])

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
                a.Inscribed = $Inscribed,
                a.Museum=$Museum,
                a.PlaceOri=$PlaceOri,
                a.Classifications=$Classifications,
                a.Medium=$Medium
        """, id=art_id,
                    Title=row.get("Title", ""),
                    Artist=row.get("Artist", ""),
                    Dynasty=row.get("Dynasty", ""),
                    CreditLine=row.get("CreditLine", ""),
                    Dimensions=row.get("Dimensions", ""),
                    Materials=row.get("Materials", ""),
                    Description=row.get("Description", ""),
                    Inscribed=row.get("Inscribed", ""),
                    Museum=row.get("Museum", ""),
                    PlaceOri=row.get("PlaceOri", ""),
                    Classifications=row.get("Classifications", ""),
                    Medium=row.get("Medium", ""),
                    )

        artist = row.get("OnlyArtist")
        if pd.notna(artist):
            session.run("""
                        MERGE (m:Artist {name: $artist})
                        WITH m
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:创作者是]->(m)
                    """, id=art_id, artist=artist.strip())

        dynasty = row.get("periods")
        if pd.notna(dynasty):
            for dynastyonly in split_multi_values(dynasty):
                if dynastyonly:
                    session.run("""
                        MERGE (d:Dynasty {name: $dynasty})
                        WITH d
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:创造年代是]->(d)
                    """, id=art_id, dynasty=dynastyonly.strip())

        dimensions = row.get("Dimensions")
        if pd.notna(dimensions):
            session.run("""
                        MERGE (m:Dimension {name: $dimensions})
                        WITH m
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:尺寸是]->(m)
                    """, id=art_id, dimensions=dimensions.strip())

        materials = row.get("Materials")
        if pd.notna(materials):
            for material in split_multi_values(materials):
                if materials:
                    session.run("""
                            MERGE (p:Material {name: $material})
                            WITH p
                            MATCH (a:Artifact {id: $id})
                            MERGE (a)-[:材质是]->(p)
                        """, id=art_id, material=material)

        museum = row.get("Museum")
        if pd.notna(museum):
            session.run("""
                        MERGE (m:Museum {name: $museum})
                        WITH m
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:现藏博物馆是]->(m)
                    """, id=art_id, museum=museum.strip())

        place = row.get("PlaceOri")
        if pd.notna(place):
            session.run("""
                MERGE (p:PlaceOri {name: $place})
                WITH p
                MATCH (a:Artifact {id: $id})
                MERGE (a)-[:来源地是]->(p)
            """, id=art_id, place=place.strip())

        classifications = row.get("Classifications")
        if pd.notna(classifications):
            session.run("""
                        MERGE (c:Classification {name: $cls})
                        WITH c
                        MATCH (a:Artifact {id: $id})
                        MERGE (a)-[:类型是]->(c)
                    """, id=art_id, cls=classifications.strip())

        mediums = row.get("Medium")
        if pd.notna(mediums):
            for med in split_multi_values(mediums):
                if med:
                    session.run("""
                               MERGE (m:Medium {name: $medium})
                               WITH m
                               MATCH (a:Artifact {id: $id})
                               MERGE (a)-[:媒介是]->(m)
                           """, id=art_id, medium=med)

        print(row.get('id'))
