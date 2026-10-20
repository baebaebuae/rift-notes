"""Build an audited Korean glossary; preserve all source numbers and formulas."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'dist/data'
# Longest phrases win; the generated exact-key glossary is checked for leftovers.
PAIRS='''
Maximum Mixed Total Damage with Fire at Will and Death's Daughter|사기 진작·죽음의 여신 강화 최대 혼합 총 피해량
Total Mixed Damage with Death's Daughter|죽음의 여신 강화 혼합 총 피해량
True Damage with Death's Daughter|죽음의 여신 고정 피해량
Total Magic Damage with Fire at Will|사기 진작 강화 총 마법 피해량
Damage with A Thousand Cuts|가위 난도질 포함 피해량
Damage to target on 67% missing hp|체력을 67% 잃은 대상 피해량
Life steal and spell vamp|생명력 흡수·주문 흡혈
Total HP/Mana Regeneration (per 5 Seconds)|5초당 총 체력·마나 재생량
HP/Mana Regenerated per 0.5 Seconds|0.5초당 체력·마나 재생량
Health Regenerated per 0.5 Seconds|0.5초당 체력 재생량
Breath of Light Flat Damage Modifier|빛의 숨결 고정 피해량 배율
Base Attack Range Scaling|기본 공격 사거리 계수
Bonus Move Speed|추가 이동 속도
Arc of Ruin Base Damage|파멸의 곡선 기본 피해량
Untouchable Shadow Dash Speed|무적의 그림자 돌진 속도
Prowl-Enhanced|수풀 배회 강화
with Infinity Edge|무한의 대검 적용 시
Grey Health|회색 체력
Critical Strike Chance|치명타 확률
Crit Chance|치명타 확률
Critical Damage|치명타 피해량
Critical Physical Damage|치명타 물리 피해량
Non-Minion Non-Sweetspot|미니언 외 대상·날 이외 부분
Non-Minion Sweetspot|미니언 외 대상·날 부분
Non-Epic Monster|일반 몬스터
Non-Champion|챔피언 외 대상
Non-Minion|미니언 외 대상
Minion/Monster|미니언·몬스터
Minion and Small Monster|미니언·소형 몬스터
Attack Damage|공격력
Attack Speed|공격 속도
Attack Range|공격 사거리
Movement Speed|이동 속도
Magic Resistance|마법 저항력
Magic Penetration|마법 관통력
Armor Penetration|방어구 관통력
Armor Reduction|방어력 감소
MR Reduction|마법 저항력 감소
Physical Damage|물리 피해량
Magic Damage|마법 피해량
True Damage|고정 피해량
Mixed Damage|혼합 피해량
Damage Reduction|피해 감소량
Heal and Shield Power|체력 회복·보호막 효과
Health Regeneration|체력 재생
Health Regenerated|체력 재생량
Life Steal|생명력 흡수
Static Cooldown|고정 재사용 대기시간
Cooldown Refund|재사용 대기시간 환급
Reduced Cooldown|감소된 재사용 대기시간
Tumble Cooldown Reduction|구르기 재사용 대기시간 감소
Health Cost|체력 소모량
Shield Strength|보호막 흡수량
Shield to Healing|보호막의 회복 전환량
Airborne Duration|공중에 뜨는 시간
Knock Up Duration|공중에 뜨는 시간
Knockup Duration|공중에 뜨는 시간
Knock Back Distance|밀려나는 거리
Root Duration|속박 지속시간
Stun Duration|기절 지속시간
Fear Duration|공포 지속시간
Taunt Duration|도발 지속시간
Silence Duration|침묵 지속시간
Blind Duration|실명 지속시간
Berserk Duration|광란 지속시간
Disable Duration|행동 불가 지속시간
Slow Duration|둔화 지속시간
Invisibility Duration|투명 지속시간
Stealth Duration|은신 지속시간
Channel Duration|정신 집중 시간
Per Subsequent Stack|후속 중첩당
per Additional Stack|추가 중첩당
per Target Death|대상 처치당
Per Champion|챔피언당
Per Monster|몬스터당
Per Minion|미니언당
Per Ally|아군당
Per Stack|중첩당
Per Second|초당
per second|초당
Per Tick|회당
Per Pass|편도
per hit|적중당
Per Hit|적중당
Per Bolt|탄환당
Per Cluster|무리당
Per Dagger|단검당
Per Wave|파동당
Per Explosion|폭발당
Per Mine|지뢰당
Per Needle|바늘당
Per Orb|구체당
Per Sphere|구체당
Per Bullet|총알당
Per Feather|깃털당
Per Shot|발사당
Per Rocket|로켓당
Per Arrow|화살당
Per Missile|투사체당
Per Spin|회전당
Per Packmate|무리 동료당
Per Flurry|연속 공격당
per Snip|가위질당
per Instance|1회당
per 20%|20%당
Per 1 Fury|분노 1당
at Max Stacks|최대 중첩 시
On Champion Hit|챔피언 적중 시
Against Champions|챔피언 대상
On-Hit|적중 시
Vs. 5 Champions|챔피언 5명 대상
First Sweetspot|1타 날 부분
Second Sweetspot|2타 날 부분
Third Sweetspot|3타 날 부분
Single-Target|단일 대상
Primary Target|주 대상
Secondary Target|보조 대상
First Cast|첫 시전
Second Cast|두 번째 시전
Third Cast|세 번째 시전
Fourth Shot|네 번째 발사
Final Snip|마지막 가위질
Initial Flame|첫 여우불
Subsequent Flame|추가 여우불
Rockets 2:5|2~5번째 로켓
Rockets 6:20|6~20번째 로켓
Number of ice segments|얼음 조각 수
Distance between individual segments|얼음 조각 사이 거리
Distance between outermost segments|양 끝 얼음 조각 사이 거리
Number of Bolts|탄환 수
Number of Recasts|재시전 횟수
Number of Traps|덫 개수
Bullets Stored|저장 총알 수
Bullet Storing Interval Time|총알 저장 주기
Wave Interval Time|파동 주기
Impact Distance to Reveal|시야 확보 범위
Demolition Threshold|철거 발동 기준
Damage Mitigated|감소시킨 피해량
Damage Transmission|전달 피해량
Damage Stored into|저장 피해량 ·
Damage Stored|저장 피해량
Stored Damage|저장 피해량
Stored|저장된
Damage Effectiveness|피해 적용 비율
Heal Portion|회복 비율
Healing Percentage|회복 비율
Heal Percentage|회복 비율
Healing Cap|회복량 상한
Healing|회복량
Healing On-Hit|적중 시 회복량
Heal|회복량
Shield|보호막
Damage|피해량
Effect Duration|효과 지속시간
Buff Duration|강화 효과 지속시간
Barrier Duration|장벽 지속시간
Shroud Duration|장막 지속시간
Path Duration|경로 지속시간
Rift Duration|균열 지속시간
Trap Duration|덫 지속시간
Zone Duration|영역 지속시간
Duration|지속시간
Mana Restored|마나 회복량
Mana Restore|마나 회복량
Mana Refunded|마나 반환량
Energy Restored|기력 회복량
Fury Gained|분노 획득량
Fury Generation|분노 생성량
Ability Haste|스킬 가속
Lethality|물리 관통력
Cripple Strength|공격 속도 감소율
Cripple|공격 속도 감소
Slow|둔화율
Resistances|방어력·마법 저항력
Health Threshold|체력 기준
Health|체력
Armor|방어력
Gold Plunder|추가 골드 획득량
Silver Serpent Plunder|추가 은화 획득량
Mist Walkers|안개 망령 수
Spiderling|새끼 거미
Spider Effects Increase|거미 효과 증가량
Voidling|공허충
Outgoing|가하는
Replicated Projectile|복제 투사체
Bounce Distance Cap|튕기는 거리 상한
Bonus Overload|추가 과부하
Outer Cone|원뿔 외곽
Primary|주 대상
Secondary|보조 대상
Self|자신
Ally|아군
Center|중심부
Subsequent|후속
Combined|합산
Capped|상한 적용
Full Stack|최대 중첩
Total|총
Maximum|최대
Minimum|최소
Minion|미니언
Monster|몬스터
Champion|챔피언
Turret|포탑
Structure|구조물
Reduced|감소된
Empowered|강화
Enhanced|강화
Increased|증가된
Modified|보정된
Evolved|진화
Expanded|확장
Bonus|추가
Additional|추가
Base|기본
Initial|최초
Final|마지막
Active|사용 효과
Passive|기본 지속 효과
Decayed|감소 후
Increase|증가량
Reduction|감소량
Decay|감쇠량
Modifier|배율
Cap|상한
Flat|고정값
Strength|강도
Size|크기
Stats|능력치
Range|사거리
Charges|충전 횟수
Stacks|중첩 수
Waves|파동 수
Arrows|화살 수
Wall Length|벽 길이
Wall Width|벽 너비
Wall Health|벽 체력
Width|너비
impassable wall|통과 불가 벽
charge|충전
Blade|칼날
Handle|손잡이
Below Threshold|기준 이하
Best Friend|단짝
Big One|대형 미사일
Bleed|출혈
Bounce|튕김
Burst Fire|집중 사격
Burst|폭발
Chomper|덫
Clone|분신
Collision|충돌
Dash|돌진
Detonation|폭발
Epicenter|중심부
Explosion|폭발
Field|영역
Flurry|연속 공격
Fracture|균열
Gigalodon|거대 상어
Glob|점액
Guppy|소형 상어
Headshot|헤드샷
Hurl|집어던지기
Hyper|슝슝
Linger|잔류
Mark|표식
Orb|구체
Overload|과부하
Poison|독
Rocket|로켓
Slash|베기
Strike|타격
Thrust|찌르기
Fissure|균열
Last Tick of|마지막 회차
'''
terms={a.lower():b for line in PAIRS.strip().splitlines() for a,b in [line.split('|',1)]}
pattern=re.compile(r'(?<![A-Za-z])(?:'+ '|'.join(re.escape(k) for k in sorted(terms,key=len,reverse=True))+r')(?![A-Za-z])',re.I)
def translate(s):return pattern.sub(lambda m:terms[m[0].lower()],s)
# Unit translations express multiplication explicitly without changing a number.
UNIT_PAIRS='''
of the target's maximum health|× 대상 최대 체력
of target's maximum health|× 대상 최대 체력
of target's current health|× 대상 현재 체력
of target's missing health|× 대상 잃은 체력
of the target's missing health|× 대상 잃은 체력
of primary target's bonus health|× 주 대상 추가 체력
of target's armor|× 대상 방어력
of turret's maximum health|× 포탑 최대 체력
of Braum's maximum health|× 브라움 최대 체력
of Zac's maximum health|× 자크 최대 체력
of her maximum health|× 자신의 최대 체력
of his maximum health|× 자신의 최대 체력
of his missing health|× 자신의 잃은 체력
of his bonus health|× 자신의 추가 체력
of Ivern's AP|× 아이번 AP
of Sona's AP|× 소나 AP
of Taric's armor|× 타릭 방어력
of Siphoning Strike stacks|× 흡수의 일격 중첩 수
of damage dealt|× 가한 피해량
of damage stored|× 저장한 피해량
of the original damage|× 원래 피해량
of expended Grit|× 소모한 투지
of maximum health|× 최대 체력
of missing health|× 잃은 체력
of missing mana|× 잃은 마나
of health lost in the past 4 seconds|최근 4초간 잃은 체력
per Overwhelm stack on the target|대상의 과다 중첩당
per Mist collected|안개 수집당
per Soul collected|영혼 수집당
per Feast stack|포식 중첩당
per Mark|표식 중첩당
based on critical strike chance|치명타 확률 비례
critical strike chance|치명타 확률
Pantheon's bonus health|판테온 추가 체력
of Sona's AP|소나 AP
bonus attack speed|추가 공격 속도
bonus magic resistance|추가 마법 저항력
bonus movement speed|추가 이동 속도
bonus armor|추가 방어력
bonus health|추가 체력
bonus mana|추가 마나
bonus AD|추가 AD
total magic resistance|총 마법 저항력
total armor|총 방어력
maximum health|최대 체력
maximum mana|최대 마나
missing health|잃은 체력
life steal|생명력 흡수
chunks of ice|개의 얼음 조각
soldiers|명의 병사
units|거리
seconds|초
Stardust|별가루
armor|방어력
per|당
'''
unitTerms={a.lower():b for line in UNIT_PAIRS.strip().splitlines() for a,b in [line.split('|',1)]}
unitPattern=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(k) for k in sorted(unitTerms,key=len,reverse=True))+r')(?![A-Za-z])',re.I)
def unit(s):return unitPattern.sub(lambda m:unitTerms[m[0].lower()],s)
labels=set();units=set();variants=set()
for c in json.loads((DATA/'index.json').read_text())['champions']:
 d=json.loads((DATA/(c['id']+'.json')).read_text())
 for f in d['formulas']:
  for v in f['variants']:
   if len(f['variants'])>1:variants.add(v['name'])
   for r in v['rows']:
    labels.add(r['attribute'])
    for m in r['modifiers']:units.update(m['units'])
# Hand-reviewed exceptions and variant names live separately for easy updates.
extraPath=ROOT/'scripts/locales/ko-exact.json'
extra=json.loads(extraPath.read_text()) if extraPath.exists() else {}
result={'labels':{s:extra.get('labels',{}).get(s,translate(s)) for s in sorted(labels)},'units':{s:extra.get('units',{}).get(s,unit(s)) for s in sorted(units)},'variants':extra.get('variants',{})}
(ROOT/'dist/data/localization-ko.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
remaining={k:{s:v for s,v in result[k].items() if re.search(r'[A-Za-z]{2,}',re.sub(r'\b(?:AP|AD)\b','',v))} for k in ['labels','units']}
print(json.dumps(remaining,ensure_ascii=False,indent=2))
print('Missing variants',json.dumps(sorted(variants-set(result['variants'])),ensure_ascii=False))
# Reviewed overrides carry the same values in both languages.
verifiedTranslations={
'정기 조각 회복 · 9중첩':'Essence Fragment heal · 9 stacks','챔피언 처치 관여 회복':'Champion takedown heal','처치 관여 인정 시간':'Takedown window','편도 피해량':'Damage per pass','왕복 총 피해량':'Total damage over both passes','피해 유형':'Damage type','첫 여우불 피해량':'First flame damage','추가 여우불 피해량':'Subsequent flame damage','단일 대상 총 피해량':'Total single-target damage','추가 이동 속도':'Bonus movement speed','마법 피해량':'Magic damage','매혹 지속시간':'Charm duration','적중 1회 피해량':'Damage per hit','기본 사용 횟수':'Base casts','1회당 공격 대상':'Targets per cast','속박 지속시간':'Root duration','표식 추가 마법 피해량':'Mark bonus magic damage','표식 유지 시간':'Mark duration',
'35–95 (레벨 비례) + 20% AP':'35–95 (based on level) + 20% AP','75–165 (레벨 비례) + 30% AP':'75–165 (based on level) + 30% AP','피해를 입힌 뒤 3초':'3s after dealing damage','갈 때 마법 / 돌아올 때 고정':'Magic on the way out / true on return','40% · 2초 동안 감소':'40% · decays over 2s','1.2 / 1.35 / 1.5 / 1.65 / 1.8초':'1.2 / 1.35 / 1.5 / 1.65 / 1.8s','3회 · 처치 관여 시 추가':'3 casts · additional casts on takedown','최대 3명':'Up to 3 targets','2초 · 최대 2명':'2s · up to 2 targets','30–200 (레벨 비례) + 35% AP':'30–200 (based on level) + 35% AP','6초':'6s'
}
verified=json.loads((DATA/'verified.json').read_text())
for champion in verified.values():
 for rows in champion['skills'].values():
  for row in rows:
   for field in ['attribute','value']:
    if field in row:row[field]=verifiedTranslations.get(row[field],row[field])
assert not re.search('[가-힣]',json.dumps(verified,ensure_ascii=False)), 'Untranslated verified value'
(DATA/'verified-en.json').write_text(json.dumps(verified,ensure_ascii=False,separators=(',',':')))
# Some official Korean patch articles contain English passages (notably 13.17).
# Translate their display text while retaining the original text and source URL.
HISTORY_PAIRS='''
Deathbringer Stance|사신 태세
Infernal Chains|지옥사슬
Mana Barrier|마나 보호막
Overdrive|폭주
Power Fist|강철 주먹
Static Field|정전기장
Cocoon|고치
Boulder Toss|돌덩이 던지기
Rampage|회오리 베기
Spirit of Dread|공포의 망령
Mounting Dread|차오르는 공포
Illumination|광채
Light Binding|빛의 속박
Lucent Singularity|광휘의 특이점
Command: Dissonance|명령: 불협화음
Blinding Assault|실명 공격
Vault|공중제비
Blast Shield|폭발 보호막
Denting Blows|찌그러뜨리기
Relentless Force|끈질긴 힘
Mana Surge|마나 쇄도
Eye of Destruction|파멸의 눈
Three Talon Strike|삼조격
Sleepy Trouble Bubble|헤롱헤롱쿨쿨방울
Cooldown Refunded on Unit Kill|유닛 처치 시 재사용 대기시간 환급
Passive Cooldown Reduction|기본 지속 효과 재사용 대기시간 감소
Heal on Third Stack|세 번째 중첩 시 회복량
Bonus Magic Damage on Basic Attacks|기본 공격 추가 마법 피해량
On-Hit Healing on Basic Attacks|기본 공격 적중 시 회복량
Damage Type|피해 유형
Attack Speed Ratio|공격 속도 계수
Base Mana Regeneration|기본 마나 재생
Base Health Regeneration|기본 체력 재생
Mana Regeneration Growth|마나 재생 증가량
Attack Damage Growth|공격력 증가량
Health Growth|체력 증가량
Armor Growth|방어력 증가량
Mana Growth|마나 증가량
Base Stats|기본 능력치
Base Health|기본 체력
Base Mana|기본 마나
Base Attack Speed|기본 공격 속도
Mana Cost|마나 소모량
Bonus Attack Speed|추가 공격 속도
Bonus Physical Damage|추가 물리 피해량
Passive Damage|기본 지속 효과 피해량
Stun Duration|기절 지속시간
Sleep Duration|수면 지속시간
Magic Resistance Reduction|마법 저항력 감소
Magic Resistance|마법 저항력
Attack Range|공격 사거리
Physical Damage|물리 피해량
Magic Damage|마법 피해량
Shield Strength|보호막 흡수량
Cooldown|재사용 대기시간
Passive|기본 지속 효과
Physical|물리
Magic|마법
Slow|둔화율
Maximum Mana|최대 마나
of Vi’s maximum health|× 바이 최대 체력
of maximum health|× 최대 체력
of Maximum Mana|× 최대 마나
based on level|레벨 비례
levels|레벨
bonus AD|추가 AD
per Mark Mark|표식당
target’s missing health|× 대상 잃은 체력
for 1 second|1초 동안
per 100 AP|/ 100 AP
seconds|초
at all ranks|모든 스킬 레벨에서
HUD|상태 표시창
Fnatic|프나틱
ALL OUT|올아웃
'''
historyTerms={a.lower():b for line in HISTORY_PAIRS.strip().splitlines() for a,b in [line.split('|',1)]}
historyPattern=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(re.escape(k) for k in sorted(historyTerms,key=len,reverse=True))+r')(?![A-Za-z])',re.I)
historyExact={
'removed Bonus Damage to Non-Champions : E no longer deals a bonus 150% AD (+125% AP) to non-champions':'삭제 · 챔피언 외 대상 추가 피해량 : E가 챔피언 외 대상에게 추가로 입히던 150% AD (+125% AP) 피해가 삭제됩니다.',
'Omnivamp : 25% (+2% of 100 bonus AD) of damage dealt ⇒ 20% of damage dealt (Note: this is still post-mitigation damage dealt)':'모든 피해 흡혈 : 가한 피해량의 25% (+추가 AD 100당 2%) ⇒ 가한 피해량의 20% (참고: 적 방어력 적용 후 실제로 가한 피해량 기준)',
}
history={}
for c in json.loads((DATA/'index.json').read_text())['champions']:
 for h in json.loads((DATA/(c['id']+'.json')).read_text())['history']:
  for ch in h['changes']:
   for field in ['title','text']:
    source=ch[field];translated=historyExact.get(source,historyPattern.sub(lambda m:historyTerms[m[0].lower()],source))
    if translated!=source:history[source]=translated
result['history']=history
(ROOT/'dist/data/localization-ko.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
assert not any(remaining.values()), 'Untranslated formula labels or units'
assert not (variants-set(result['variants'])), 'Missing Korean variant names'
print('Korean glossary:',len(result['labels']),'labels,',len(result['units']),'units,',len(result['variants']),'variants,',len(history),'patch strings')
