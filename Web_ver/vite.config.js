import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

export default defineConfig({
  base: './',
  plugins: [viteSingleFile()],
  server: { fs: { allow: ['..'] } }, // docs/*.md live one level up
  worker: { format: 'es', plugins: () => [] },
  test: { include: ['tests/**/*.test.js'] },
});
