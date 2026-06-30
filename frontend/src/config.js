/** 服务器基地址：浏览器下为空走 Vite proxy；Electron 下由 preload 注入 */
export const SERVER_URL = (typeof window !== 'undefined' && window.__SERVER_URL__) || ''
