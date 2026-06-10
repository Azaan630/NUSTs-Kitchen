import{j as e}from"./animations-BMjfS7F_.js";import{c as s,u as d,B as r}from"./index-FD66O-8v.js";import{d as m}from"./vendor-DZLw6YzZ.js";import"./charts-DkYD5_7t.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const c=s("FileQuestion",[["path",{d:"M12 17h.01",key:"p32p05"}],["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z",key:"1mlx9k"}],["path",{d:"M9.1 9a3 3 0 0 1 5.82 1c0 2-3 3-3 3",key:"mhlwft"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const i=s("House",[["path",{d:"M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8",key:"5wwlr5"}],["path",{d:"M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",key:"1d0kgt"}]]);function f(){const a=m(),{isAuthenticated:o,role:t}=d(),n=o?t==="Admin"?"/admin/dashboard":t==="Staff"?"/staff/today":"/student/today":"/login";return e.jsxs("div",{className:"min-h-screen flex flex-col items-center justify-center p-8 text-center",children:[e.jsx("div",{className:"flex h-20 w-20 items-center justify-center rounded-full bg-muted",children:e.jsx(c,{className:"h-10 w-10 text-muted-foreground"})}),e.jsx("h1",{className:"mt-6 text-4xl font-bold",children:"404"}),e.jsx("p",{className:"mt-2 text-lg text-muted-foreground",children:"Page not found"}),e.jsx("p",{className:"mt-1 text-sm text-muted-foreground",children:"The page you're looking for doesn't exist or has been moved."}),e.jsxs(r,{className:"mt-6 gap-2",onClick:()=>a(n),children:[e.jsx(i,{className:"h-4 w-4"})," Go Home"]})]})}export{f as NotFoundPage};
