import sys, json, time
sys.path.insert(0,'/home/nir/crystal-balls')
from pipeline import common
R='/home/nir/crystal-balls/data/rounds/'
f14=json.load(open(R+'2026-10-02/countries/IL.json'))
f17=json.load(open(R+'2026-10-17/countries/IL.json'))
S=common.load_settings()
items=f14['questions']['items']; ids=[q['id'] for q in items]
truth={q['id']:q['outcome'] for q in f17['wind']['questions']}
assert [q['text'] for q in f17['wind']['questions']]==[q['text'] for q in items]
pos=common.position_as_text(f14['position'],'2026-10-02')
vel=common.velocity_as_text(f14['velocity'])
wind=common.wind_v2_as_text(f14['wind'])
raw=open('/home/nir/crystal-balls/data/legacy/round-1/Israel.txt',encoding='utf-8').read()
prev=" ".join(raw.split()[:300])
common_vars={"COUNTRY":"Israel","HORIZON_START":"2026-10-02","HORIZON_END":"2026-10-21","HEADLINES":pos,"QUESTIONS":common.questions_as_text(items)}
t=time.time()
print(time.strftime('%H:%M:%S'),'naive start',flush=True)
n=common.llm_json("05_naive_answers.txt",common_vars,lambda o:common.validate_answers(o,ids,crystal=False),"test_naive","IL",round_id="2026-10-02",settings=S)
print(time.strftime('%H:%M:%S'),'naive done',int(time.time()-t),'s; crystal start',flush=True)
cv=dict(common_vars,ROUND="2026-10-02",CURRENT_POSITION=pos,PREVIOUS_ROUND="2026-09-15",VELOCITY=vel,WIND=wind,PREVIOUS_CRYSTAL_SUMMARY=prev)
c=common.llm_json("06_crystal_answers.txt",cv,lambda o:common.validate_answers(o,ids,crystal=True),"test_crystal","IL",round_id="2026-10-02",settings=S)
print(time.strftime('%H:%M:%S'),'crystal done',flush=True)
na={a['id']:a['answer'] for a in n['answers']}; ca={a['id']:a['answer'] for a in c['answers']}
res={'truth':truth,'naive':na,'crystal':ca}
json.dump({'naive':n,'crystal':c,'truth':truth},open('/tmp/opencode/test_il.json','w'),indent=1)
for i in ids: print(i,'truth',truth[i],'naive',na[i],'crystal',ca[i])
for nm,a in(('naive',na),('crystal',ca)):
    j=[i for i in ids if truth[i] in('YES','NO')]
    print(nm,sum(a[i]==truth[i] for i in j),'of',len(j))
print('TEST DONE',flush=True)
