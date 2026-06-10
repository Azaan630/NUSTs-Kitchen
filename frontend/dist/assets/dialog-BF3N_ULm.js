import{c as i,S as t}from"./index-CqUj8vbM.js";import{j as a}from"./animations-BMjfS7F_.js";import{a as l}from"./vendor-DZLw6YzZ.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const u=i("Plus",[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const n=i("X",[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]]);function x({open:s,onOpenChange:e,children:r}){const o=l.useCallback(c=>{c.key==="Escape"&&e(!1)},[e]);return l.useEffect(()=>(s&&(document.addEventListener("keydown",o),document.body.style.overflow="hidden"),()=>{document.removeEventListener("keydown",o),document.body.style.overflow=""}),[s,o]),s?a.jsxs("div",{className:"fixed inset-0 z-50 flex items-center justify-center p-4",children:[a.jsx("div",{className:"fixed inset-0 bg-black/50 backdrop-blur-sm animate-fade-in",onClick:()=>e(!1)}),a.jsxs("div",{role:"dialog","aria-modal":"true",className:"relative z-50 w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-xl border bg-card p-6 shadow-2xl mx-auto animate-scale-in scrollbar-thin",children:[a.jsx("button",{onClick:()=>e(!1),className:"absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2","aria-label":"Close dialog",children:a.jsx(n,{className:"h-4 w-4"})}),r]})]}):null}const g=({className:s,...e})=>a.jsx("div",{className:t("flex flex-col space-y-1.5 text-center sm:text-left mb-4 pr-8",s),...e}),p=({className:s,...e})=>a.jsx("h2",{className:t("text-lg font-semibold leading-none tracking-tight",s),...e}),b=({className:s,...e})=>a.jsx("p",{className:t("text-sm text-muted-foreground",s),...e}),y=({className:s,...e})=>a.jsx("div",{className:t("flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 mt-6 gap-2",s),...e});export{x as D,u as P,n as X,g as a,p as b,b as c,y as d};
