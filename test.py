import hashlib

def generate_color_from_xorg_key(xorg_key):
  """Génère un code couleur hexadécimal à partir d'une clé Xorg.

  Args:
    xorg_key: La clé Xorg à utiliser.

  Returns:
    Une chaîne de caractères représentant le code couleur hexadécimal.
  """

  # Choisir une fonction de hachage (ici, SHA-256)
  hash_object = hashlib.sha256(xorg_key.encode('utf-8'))
  hex_dig = hash_object.hexdigest()

  # Prendre les 6 premiers caractères du hachage pour former le code couleur
  color_hex = f"#{hex_dig[:6]}"

  return color_hex

# Exemple d'utilisation :
xorg_key = "ma_cle_xorg"
color = generate_color_from_xorg_key(xorg_key)
print(color)