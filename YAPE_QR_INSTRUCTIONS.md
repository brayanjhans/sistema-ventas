# Instrucciones para agregar el QR de Yape

## Ubicación del archivo
El QR de Yape debe reemplazar el placeholder en:
**Archivo:** `frontend/components/YapePaymentModal.tsx`
**Línea:** 107

## Pasos para agregar tu QR:

1. **Guarda tu imagen QR** en la carpeta pública de Next.js:
   ```
   frontend/public/yape-qr.png
   ```

2. **Reemplaza el placeholder** en `YapePaymentModal.tsx`:

   **Busca esto (línea 107):**
   ```tsx
   <div className="w-48 h-48 mx-auto mb-4 bg-gray-100 rounded-xl flex items-center justify-center">
       <p className="text-neutral-400 text-sm">QR de Yape aquí</p>
   </div>
   ```

   **Cámbialo por:**
   ```tsx
   <div className="w-48 h-48 mx-auto mb-4 rounded-xl overflow-hidden">
       <img 
           src="/yape-qr.png" 
           alt="QR Yape" 
           className="w-full h-full object-contain"
       />
   </div>
   ```

3. **Guarda el archivo** y el QR se mostrará automáticamente

## Alternativa (si tienes múltiples cuentas):
Puedes crear una configuración de ajustes donde el admin pueda cambiar el número y el QR desde el panel de administración.

## Número actualizado:
✅ Ya actualicé el número a **939 882 147** en el código
