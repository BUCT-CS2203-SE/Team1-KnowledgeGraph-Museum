from neo4j import GraphDatabase
import pandas as pd

# CSV 路径
artifact_path = 'your_artifact_data.csv'  # 包含 id/title、category、museum 等字段
triples_path = 'period_triples.csv'  # 三元组 subject, relation, object

# Neo4j连接
# 连接 Neo4j 数据库
NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Cs22032025"
driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))

# 加载数据
artifact_df = pd.read_csv(artifact_path)
triples_df = pd.read_csv(triples_path)

# 指定哪些字段是直接作为属性附在 Artifact 上的
artifact_attributes = ['title', 'Museum', 'Artist', 'Classifications', 'Material', 'Dimensions']

with driver.session() as session:
    for _, row in artifact_df.iterrows():
        artifact_id = f"id:{row['id']}" if 'id' in row else row['title']

        # 动态构造 SET 子句（属性绑定）
        props = {k: row[k] for k in artifact_attributes if k in row and pd.notna(row[k])}
        set_clause = ", ".join([f"a.{k} = ${k}" for k in props])

        query = f"""
            MERGE (a:Artifact {{id: $artifact_id}})
            SET {set_clause}
        """
        session.run(query, artifact_id=artifact_id, **props)

    # 导入三元组：Artifact 与 Period 的 has_period 关系
    for _, row in triples_df.iterrows():
        subject = row['subject']
        period = row['object']

        session.run("""
            MERGE (p:Period {name: $period})
            WITH p
            MATCH (a:Artifact {id: $subject})
            MERGE (a)-[:所处年代是]->(p)
        """, subject=subject, period=period)
