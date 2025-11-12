/// <reference types="vite/client" />

/**
 * Declaración de tipos para las variables de entorno de Vite.
 * Extiende la interfaz ImportMetaEnv con las variables personalizadas del proyecto.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

/**
 * Extiende la interfaz ImportMeta para incluir env.
 */
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

