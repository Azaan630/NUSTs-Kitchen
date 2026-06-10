import{j as e}from"./animations-BMjfS7F_.js";import{a as l}from"./vendor-DZLw6YzZ.js";import{c as i,S as o,B as g,an as J}from"./index-CqUj8vbM.js";import{I as K}from"./input-CDzI6BDe.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Q=i("ChevronDown",[["path",{d:"m6 9 6 6 6-6",key:"qrunsl"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const W=i("ChevronRight",[["path",{d:"m9 18 6-6-6-6",key:"mthhwq"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const X=i("ChevronUp",[["path",{d:"m18 15-6-6-6 6",key:"153udz"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Y=i("ChevronsLeft",[["path",{d:"m11 17-5-5 5-5",key:"13zhaf"}],["path",{d:"m18 17-5-5 5-5",key:"h8a8et"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const Z=i("ChevronsRight",[["path",{d:"m6 17 5-5-5-5",key:"xnjwq"}],["path",{d:"m13 17 5-5-5-5",key:"17xmmf"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $=i("ChevronsUpDown",[["path",{d:"m7 15 5 5 5-5",key:"1hf1tw"}],["path",{d:"m7 9 5-5 5 5",key:"sgt6xg"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ee=i("Inbox",[["polyline",{points:"22 12 16 12 14 15 10 15 8 12 2 12",key:"o97t9d"}],["path",{d:"M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z",key:"oot6mr"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ae=i("Search",[["circle",{cx:"11",cy:"11",r:"8",key:"4ej97u"}],["path",{d:"m21 21-4.3-4.3",key:"1qie3q"}]]),T=l.forwardRef(({className:t,...s},r)=>e.jsx("div",{className:"relative w-full overflow-auto",children:e.jsx("table",{ref:r,className:o("w-full caption-bottom text-sm",t),...s})}));T.displayName="Table";const M=l.forwardRef(({className:t,...s},r)=>e.jsx("thead",{ref:r,className:o("[&_tr]:border-b",t),...s}));M.displayName="TableHeader";const R=l.forwardRef(({className:t,...s},r)=>e.jsx("tbody",{ref:r,className:o("[&_tr:last-child]:border-0",t),...s}));R.displayName="TableBody";const se=l.forwardRef(({className:t,...s},r)=>e.jsx("tfoot",{ref:r,className:o("border-t bg-muted/50 font-medium [&>tr]:last:border-b-0",t),...s}));se.displayName="TableFooter";const w=l.forwardRef(({className:t,...s},r)=>e.jsx("tr",{ref:r,className:o("border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted",t),...s}));w.displayName="TableRow";const D=l.forwardRef(({className:t,...s},r)=>e.jsx("th",{ref:r,className:o("h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0",t),...s}));D.displayName="TableHead";const z=l.forwardRef(({className:t,...s},r)=>e.jsx("td",{ref:r,className:o("p-4 align-middle [&:has([role=checkbox])]:pr-0",t),...s}));z.displayName="TableCell";const te=l.forwardRef(({className:t,...s},r)=>e.jsx("caption",{ref:r,className:o("mt-4 text-sm text-muted-foreground",t),...s}));te.displayName="TableCaption";function S({className:t,...s}){return e.jsx("div",{className:o("animate-pulse rounded-md bg-muted",t),...s})}function re({icon:t=ee,title:s,description:r,action:x,className:p}){return e.jsxs("div",{className:o("flex flex-col items-center justify-center py-12 text-center",p),children:[e.jsx("div",{className:"flex h-16 w-16 items-center justify-center rounded-full bg-muted",children:e.jsx(t,{className:"h-8 w-8 text-muted-foreground"})}),e.jsx("h3",{className:"mt-4 text-lg font-semibold",children:s}),r&&e.jsx("p",{className:"mt-1 text-sm text-muted-foreground max-w-sm",children:r}),x&&e.jsx("div",{className:"mt-4",children:x})]})}function ie({columns:t,data:s,keyExtractor:r,searchable:x=!1,searchKeys:p,searchPlaceholder:L="Search...",pageSize:q=10,isLoading:H=!1,emptyMessage:I="No data found",emptyDescription:P,emptyAction:B,onRowClick:b,pageSizeOptions:U=[5,10,20,50]}){const[c,E]=l.useState(null),[j,k]=l.useState("asc"),[N,F]=l.useState(""),[_,m]=l.useState(0),[h,A]=l.useState(q),v=l.useMemo(()=>{if(!N||!p)return s;const a=N.toLowerCase();return s.filter(n=>p.some(y=>String(n[y]??"").toLowerCase().includes(a)))},[s,N,p]),u=l.useMemo(()=>c?[...v].sort((a,n)=>{const y=a[c]??"",G=n[c]??"",C=String(y).localeCompare(String(G),void 0,{numeric:!0});return j==="asc"?C:-C}):v,[v,c,j]),f=Math.max(1,Math.ceil(u.length/h)),d=Math.min(_,f-1),O=u.slice(d*h,(d+1)*h),V=a=>{c===a?k(n=>n==="asc"?"desc":"asc"):(E(a),k("asc")),m(0)};return H?e.jsxs("div",{className:"space-y-4",children:[x&&e.jsx(S,{className:"h-10 w-64"}),e.jsx("div",{className:"rounded-md border",children:e.jsx("div",{className:"p-4 space-y-3",children:Array.from({length:5}).map((a,n)=>e.jsx(S,{className:"h-10 w-full"},n))})})]}):u.length===0?e.jsx(re,{title:I,description:P,action:B}):e.jsxs("div",{className:"space-y-4",children:[x&&e.jsxs("div",{className:"relative max-w-sm",children:[e.jsx(ae,{className:"absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"}),e.jsx(K,{placeholder:L,value:N,onChange:a=>{F(a.target.value),m(0)},className:"pl-9"})]}),e.jsx("div",{className:"rounded-md border overflow-hidden",children:e.jsx("div",{className:"overflow-x-auto scrollbar-thin",children:e.jsxs(T,{children:[e.jsx(M,{children:e.jsx(w,{children:t.map(a=>e.jsx(D,{className:o(a.sortable&&"cursor-pointer select-none",a.hideOnMobile&&"hidden md:table-cell",a.className),onClick:a.sortable?()=>V(a.key):void 0,"aria-sort":a.sortable&&c===a.key?j==="asc"?"ascending":"descending":void 0,children:e.jsxs("div",{className:"flex items-center gap-1",children:[a.header,a.sortable&&e.jsx("span",{className:"shrink-0",children:c===a.key?j==="asc"?e.jsx(X,{className:"h-4 w-4"}):e.jsx(Q,{className:"h-4 w-4"}):e.jsx($,{className:"h-4 w-4 opacity-30"})})]})},a.key))})}),e.jsx(R,{children:O.map(a=>e.jsx(w,{className:o(b&&"cursor-pointer"),onClick:()=>b==null?void 0:b(a),children:t.map(n=>e.jsx(z,{className:o(n.hideOnMobile&&"hidden md:table-cell",n.className),children:n.render?n.render(a):a[n.key]},n.key))},r(a)))})]})})}),e.jsxs("div",{className:"flex flex-col sm:flex-row items-center justify-between gap-4",children:[e.jsxs("p",{className:"text-sm text-muted-foreground order-2 sm:order-1",children:[d*h+1,"–",Math.min((d+1)*h,u.length)," of"," ",u.length]}),e.jsxs("div",{className:"flex items-center gap-2 order-1 sm:order-2",children:[e.jsx("select",{value:h,onChange:a=>{A(Number(a.target.value)),m(0)},className:"h-8 rounded-md border border-input bg-background px-2 text-xs","aria-label":"Rows per page",children:U.map(a=>e.jsxs("option",{value:a,children:[a," / page"]},a))}),e.jsxs("div",{className:"flex gap-1",children:[e.jsx(g,{variant:"outline",size:"icon-sm",onClick:()=>m(0),disabled:d===0,"aria-label":"First page",children:e.jsx(Y,{className:"h-4 w-4"})}),e.jsx(g,{variant:"outline",size:"icon-sm",onClick:()=>m(a=>Math.max(0,a-1)),disabled:d===0,"aria-label":"Previous page",children:e.jsx(J,{className:"h-4 w-4"})}),e.jsx(g,{variant:"outline",size:"icon-sm",onClick:()=>m(a=>Math.min(f-1,a+1)),disabled:d>=f-1,"aria-label":"Next page",children:e.jsx(W,{className:"h-4 w-4"})}),e.jsx(g,{variant:"outline",size:"icon-sm",onClick:()=>m(f-1),disabled:d>=f-1,"aria-label":"Last page",children:e.jsx(Z,{className:"h-4 w-4"})})]})]})]})]})}export{Q as C,ie as D};
