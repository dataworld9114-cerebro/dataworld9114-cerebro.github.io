const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const s=fs.readFileSync('docs/algorithm.html','utf8');
const a=s.indexOf('const COMPARE_DATA=')+19,b=s.indexOf(';\nconst CMP_REQ',a);
const d=JSON.parse(s.slice(a,b)).v08;
const aa=s.indexOf('const CMP_SA='),bb=s.indexOf(';',aa),ctx={};
vm.runInNewContext(s.slice(aa,bb+1).replace('const CMP_SA=','this.aliases='),ctx);
const aliases=ctx.aliases;
const norm=v=>String(v||'').toLowerCase().replace(/’/g,"'").replace(/[^a-z0-9가-힣]/g,'');
const terms=x=>[x.field,((x.desc||'').match(/\(([^)]+)\)/)||[])[1]||'',...(aliases[x.field]||[])].map(norm).filter(Boolean);
const matches=(x,h)=>terms(x).includes(norm(h.header))||terms(x).includes(norm(h.label));
const failures=[];
for(const [pkg,books] of Object.entries(d.excelBioSample))for(const [sub,book] of Object.entries(books)){
  const items=(pkg==='standard'?d.standardSampleItems:[...d.mimsSampleItems,...d.standardSampleItems]);
  const required=book.headers.filter(h=>String(h.excelReq).startsWith('M'));
  const active=items.filter(x=>{
    const r=String((x.reqMap||{})[sub]||'-').trim();
    return (r&&r!=='-')||required.some(h=>matches(x,h));
  });
  for(const h of book.headers.filter(h=>String(h.excelReq).startsWith('M'))){
    if(active.some(x=>matches(x,h)))continue;
    const inactive=items.find(x=>matches(x,h));
    failures.push({pkg,sub,col:h.col,header:h.header,standard:inactive?.field||null});
  }
}
if(process.argv.includes('--report'))console.log(JSON.stringify(failures,null,2));
else assert.deepEqual(failures,[],`Required Excel headers unmatched:\n${JSON.stringify(failures,null,2)}`);
