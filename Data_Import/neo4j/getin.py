import csv
from neo4j import GraphDatabase

# 你的 Neo4j 数据库连接配置
NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "Cs22032025"

# CSV 文件路径
input_csv = '../datasets_museum/china.csv'  # 替换为你的输入CSV文件路径

# 连接 Neo4j 数据库
driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))


def create_knowledge_graph():
    with driver.session() as session:
        # 清空现有数据库，防止重复导入
        session.run("MATCH (n) DETACH DELETE n")

        # 读取CSV并构建三元组
        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title = row['Title']
                time = row['Dynasty']
                artist = row['Artist']
                material = row['Materials']
                dimensions = row['Dimensions']
                category = row['Classifications']
                museum = row['museum']

                # 只在第一次创建 Artifact 节点
                session.run("""
                    MERGE (t:Artifact {name: $title, type: 'Artifact'})
                """, title=title)

                # 创建关联节点和关系
                if time and time != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (d:Time {name: $time, type: 'Time'})
                        MERGE (t)-[:处于的年代]->(d)
                    """, title=title, time=time)

                if artist and artist != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (a:Artist {name: $artist, type: 'Artist'})
                        MERGE (t)-[:创作者为]->(a)
                    """, title=title, artist=artist)

                if material and material != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (m:Material {name: $material, type: 'Material'})
                        MERGE (t)-[:材质为]->(m)
                    """, title=title, material=material)

                if dimensions and dimensions != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (s:Dimensions {name: $dimensions, type: 'Dimensions'})
                        MERGE (t)-[:尺寸为]->(s)
                    """, title=title, dimensions=dimensions)

                if category and category != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (c:Category {name: $category, type: 'Category'})
                        MERGE (t)-[:类型为]->(c)
                    """, title=title, category=category)

                if museum and museum != "NULL":
                    session.run("""
                        MATCH (t:Artifact {name: $title})
                        MERGE (m:Museum {name: $museum, type: 'Museum'})
                        MERGE (t)-[:位于]->(m)
                    """, title=title, museum=museum)

    print("✅ 知识图谱已成功导入 Neo4j。")


create_knowledge_graph()
driver.close()