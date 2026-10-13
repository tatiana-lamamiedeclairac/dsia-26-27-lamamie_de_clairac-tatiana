# Métricas que he calcualado:
# Total de likes -> Cuántas valoraciones positivas hay en el dataset
# Likes por país -> Cuántas valoraciones positivas ha recibido cada país
# Likes por destino -> Cuántas valoraciones positivas ha recibido cada destino

def total_likes(df):
    total = df["liked"].sum()
    return total

def likes_by_country(df):
    result = df.groupby("country")["liked"].sum()
    return result

def likes_by_destination(df):
    result = df.groupby("destination")["liked"].sum()
    return result

