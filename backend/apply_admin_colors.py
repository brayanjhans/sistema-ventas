import re
import os

# Paths to update
pages = [
    r'C:\laragon\www\sistema-ventas\frontend\app\admin\productos\page.tsx',
    r'C:\laragon\www\sistema-ventas\frontend\app\admin\pedidos\page.tsx',
    r'C:\laragon\www\sistema-ventas\frontend\app\admin\stock\page.tsx',
    r'C:\laragon\www\sistema-ventas\frontend\app\admin\configuracion\page.tsx'
]

# Color replacements
replacements = [
    # Buttons
    (r'bg-blue-600', 'bg-primary-600'),
    (r'bg-blue-700', 'bg-primary-700'),
    (r'hover:bg-blue-700', 'hover:bg-primary-700'),
    (r'hover:bg-blue-800', 'hover:bg-primary-800'),
    (r'text-blue-600', 'text-primary-600'),
    (r'text-blue-700', 'text-primary-700'),
    (r'text-blue-800', 'text-primary-800'),
    
    # Focus rings
    (r'focus:ring-blue-500', 'focus:ring-primary-500'),
    (r'focus:border-blue-500', 'focus:border-primary-500'),
    
    # Grays to neutrals
    (r'text-gray-900', 'text-neutral-900'),
    (r'text-gray-600', 'text-neutral-600'),
    (r'text-gray-700', 'text-neutral-700'),
    (r'border-gray-300', 'border-neutral-300'),
    
    # Green to success
    (r'bg-green-100', 'bg-success-100'),
    (r'text-green-800', 'text-success-800'),
    (r'text-green-600', 'text-success-600'),
    
    # Typography
    (r'text-3xl font-bold', 'text-4xl font-display font-bold text-neutral-900'),
]

for page_path in pages:
    if not os.path.exists(page_path):
        print(f"❌ No encontrado: {page_path}")
        continue
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Actualizado: {page_path}")
    else:
        print(f"ℹ️  Sin cambios: {page_path}")

print("\n✨ Rediseño pink/rose aplicado a todas las páginas admin!")
