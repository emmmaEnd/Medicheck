from supabase import create_client, Client

URL = "https://ivwwwdbibjwmvipoyghv.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml2d3d3ZGJpYmp3bXZpcG95Z2h2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMzMzA1MTUsImV4cCI6MjA3ODkwNjUxNX0.1AGQu4h8W0IViYIZJJpR5vJysOXfJXTtirs1AGrqU5g"

supabase: Client = create_client(URL, KEY)

def supabase_login(usuario: str, contrasena: str) -> bool:
    result = supabase.table("medico").select("*").eq("usuario", usuario).eq("contrasena", contrasena).execute()

    return len(result.data) > 0
