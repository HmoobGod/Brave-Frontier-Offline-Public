"""v0.54: make source-header sprite strip invisible and bind EXP to real v7 demo data.

Browser DOM assertions test the responsive crop, truthfully unavailable energy,
reward updates and that none of the prior saved game state is modified.
"""
from pathlib import Path
import hashlib,shutil
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parent
ASSETS=R/'app/src/main/assets'
addon=(ASSETS/'bf054_header_status.js').read_text('utf-8')
assert addon.count('/* BF_HEADER_STATUS_FIDELITY_V054 */')==1
assert 'bf_global_offline_demo_v7' not in addon, 'header overlay must never write saves'
assert 'localStorage.setItem' not in addon
assert 'min-height:44px' in addon
assert 'Number.isSafeInteger(P?.level)' in addon and 'Number.isSafeInteger(P.exp)' in addon
assert "P.exp>=levelFloor" in addon and "5*(P.level-1)*P.level/2" in addon
java=(R/'app/src/main/java/org/bravefrontier/offline/MainActivity.java').read_text('utf-8')
assert java.count('readPackagedText("bf054_header_status.js")')==1
assert java.index('readPackagedText("bf_home_nav.js")') < java.index('readPackagedText("bf054_header_status.js")')
html=(ASSETS/'index.html').read_text('utf-8')

with sync_playwright() as pw:
    browser=pw.chromium.launch(
        headless=True,
        executable_path=shutil.which('chromium') or shutil.which('google-chrome')
                        or shutil.which('google-chrome-stable'),
        args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate("""() => {
      const saved={};let writes=0;window.__headerWrites=()=>writes;
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>saved[k]??null,setItem:(k,v)=>{writes++;saved[k]=String(v)},
        removeItem:k=>{writes++;delete saved[k]},key:i=>Object.keys(saved)[i]??null,
        get length(){return Object.keys(saved).length}}});
      window.alert=()=>{};window.confirm=()=>true;
      HTMLMediaElement.prototype.load=()=>{};
      HTMLMediaElement.prototype.pause=()=>{};
      HTMLMediaElement.prototype.play=()=>Promise.resolve();
    }""")
    page.set_content(html,wait_until='load',timeout=90000)
    initial=page.evaluate("""() => ({version:P.version,exp:P.exp,level:P.level,
        zel:P.zel,karma:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),
        roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad)})""")
    page.add_style_tag(path=str(ASSETS/'bf_home_nav.css'))
    page.add_script_tag(path=str(ASSETS/'bf_home_nav.js'))
    # Measure the unchanged base Home layout at 320px before this add-on.
    # The pre-existing 1px overhang belongs to .bf-shell-head, not the footer.
    # The shared header source fix is tracked by PR #388. This isolated
    # status-add-on regression must not introduce any additional scroll width.
    page.set_viewport_size({'width':320,'height':844})
    base_scroll_width=page.evaluate('document.documentElement.scrollWidth')
    page.set_viewport_size({'width':390,'height':844})
    page.add_script_tag(path=str(ASSETS/'bf054_header_status.js'))
    assert page.evaluate('BF_homeNav.current')=='home'
    assert page.evaluate('BF054HeaderStatus.originalHeaderCropped') is True
    assert page.evaluate('BF054HeaderStatus.energyAvailable') is False
    assert page.locator('#bf054-exp').count()==1
    assert page.locator('#bf054-energy').count()==1
    assert page.locator('#bf054-exp-text').inner_text()=='0 / 5'
    assert page.locator('#bf054-energy').inner_text()=='— / —'
    assert 'not simulated' in page.locator('#bf054-energy').get_attribute('title').lower()
    assert page.locator('#bf054-exp').get_attribute('aria-valuenow')=='0'
    assert page.locator('#bf054-exp').get_attribute('aria-valuemax')=='5'
    css=page.evaluate("""() => {
       const el=document.querySelector('.bf-shell-head'),style=getComputedStyle(el);
       const bounds=el.getBoundingClientRect();
       return {width:bounds.width,height:bounds.height,backgroundSize:style.backgroundSize,
         backgroundPosition:style.backgroundPosition,overflow:style.overflow,
         oldImage:style.backgroundImage.includes('header_ui3.png')}
    }""")
    assert css['oldImage'] and css['overflow']=='hidden',css
    assert 0.264 < css['height']/css['width'] < 0.279, css
    assert css['backgroundSize']=='100% auto',css
    assert page.evaluate('BF054HeaderStatus.state.percent')==0
    # The new native Home disclosure is closed by default, read-only and
    # reports genuinely unavailable Energy rather than fake regeneration.
    details=page.locator('#bf054-home-details')
    assert details.count()==1
    assert details.get_attribute('open') is None
    assert 'Energy unavailable' in page.locator('#bf054-home-values').text_content()
    details.locator('summary').click()
    assert details.get_attribute('open') is not None
    assert 'Demo Lv.1' in page.locator('#bf054-home-values').inner_text()
    assert 'Zel 0' in page.locator('#bf054-home-values').inner_text()
    assert page.locator('#bf054-home-next-level').inner_text()==(
        'Next demo level 2 · 5 EXP remaining · Total demo EXP 0.')
    for width in (320,390,540):
        page.set_viewport_size({'width':width,'height':844})
        summary_bounds=details.locator('summary').bounding_box()
        assert summary_bounds and summary_bounds['height']>=44,(width,summary_bounds)
    # Transient malformed v7 local data must not be represented as level one.
    # All mutations remain in test memory and are explicitly restored.
    invalid=page.evaluate("""()=>{
      const oldLevel=P.level,oldExp=P.exp,oldVersion=P.version;
      const save=localStorage.getItem('bf_global_offline_demo_v7');
      const result={};
      const inspect=()=>{
        const state=BF054HeaderStatus.refresh();
        return {state:BF054HeaderStatus.state,
          text:document.getElementById('bf054-exp-text').textContent,
          aria:document.getElementById('bf054-exp').getAttribute('aria-valuetext'),
          home:document.getElementById('bf054-home-values').textContent,
          next:document.getElementById('bf054-home-next-level').textContent};
      };
      try{
        P.level=0;result.zeroLevel=inspect();
        P.level='2';result.stringLevel=inspect();
        P.level=100;result.outOfRangeLevel=inspect();
        P.level=1;P.exp=-3;result.negativeExp=inspect();
        P.exp=NaN;result.nanExp=inspect();
        P.exp=Infinity;result.infiniteExp=inspect();
        P.exp='13';result.stringExp=inspect();
        P.exp=0;P.version=6;result.invalidVersion=inspect();
        // v456: EXP is cumulative; a level with too little total EXP
        // is malformed even when both numbers are individually valid.
        P.version=7;P.level=2;P.exp=4;result.level2MissingExp=inspect();
        P.level=3;P.exp=14;result.level3MissingExp=inspect();
        P.level=99;P.exp=24254;result.level99MissingExp=inspect();
        P.level=1;P.exp=5;result.level1AtCeiling=inspect();
        P.level=2;P.exp=15;result.level2AtCeiling=inspect();
        P.level=3;P.exp=30;result.level3AtCeiling=inspect();
        P.level=98;P.exp=24255;result.level98AtCeiling=inspect();
        P.level=1;P.exp=4;result.level1BelowCeiling=inspect();
        P.level=2;P.exp=14;result.level2BelowCeiling=inspect();
        P.level=98;P.exp=24254;result.level98BelowCeiling=inspect();
        P.level=2;P.exp=5;result.level2Floor=inspect();
        P.level=3;P.exp=15;result.level3Floor=inspect();
        P.level=99;P.exp=24255;result.level99Floor=inspect();
      }finally{
        P.level=oldLevel;P.exp=oldExp;P.version=oldVersion;
        BF054HeaderStatus.refresh();
      }
      result.saveUnchanged=localStorage.getItem('bf_global_offline_demo_v7')===save;
      result.normal=BF054HeaderStatus.state.valid;
      return result;
    }""")
    for kind in ('zeroLevel','stringLevel','outOfRangeLevel','negativeExp',
                 'nanExp','infiniteExp','stringExp','invalidVersion',
                 'level2MissingExp','level3MissingExp','level99MissingExp',
                 'level1AtCeiling','level2AtCeiling','level3AtCeiling',
                 'level98AtCeiling'):
        item=invalid[kind]
        assert item['state']['valid'] is False,(kind,item)
        assert item['text']=='— / —',(kind,item)
        assert 'unavailable' in item['aria'],(kind,item)
        assert 'Lv./EXP unavailable' in item['home'],(kind,item)
        assert item['next']=='Next demo level unavailable · invalid local EXP state.',(kind,item)
    for kind,expected in (('level2Floor','0 / 10'),
                          ('level3Floor','0 / 15'),
                          ('level1BelowCeiling','4 / 5'),
                          ('level2BelowCeiling','9 / 10'),
                          ('level98BelowCeiling','489 / 490'),
                          ('level99Floor','MAX')):
        item=invalid[kind]
        assert item['state']['valid'] is True,(kind,item)
        assert item['text']==expected,(kind,item)
    assert invalid['saveUnchanged'] and invalid['normal'],invalid
    assert invalid['level2Floor']['next']==(
        'Next demo level 3 · 10 EXP remaining · Total demo EXP 5.')
    assert invalid['level3Floor']['next']==(
        'Next demo level 4 · 15 EXP remaining · Total demo EXP 15.')
    assert invalid['level99Floor']['next']==(
        'Demo maximum level 99 · Total demo EXP 24,255.')
    for kind in ('level1BelowCeiling','level2BelowCeiling','level98BelowCeiling'):
        assert '1 EXP remaining' in invalid[kind]['next'],(kind,invalid[kind])
    # v460: the nav header must not present stale rendered strings as actual
    # save values. Route navigation itself copies core text into the header;
    # the read-only validator must immediately override that false display.
    header_probe=page.evaluate("""() => {
      const ids=['plevel','pzel','pkarma'];
      const prev=Object.fromEntries(
        ['version','level','exp','zel','karma'].map(k=>[k,P[k]]));
      const rendered=Object.fromEntries(ids.map(id=>
        [id,document.getElementById(id).textContent]));
      const before=JSON.stringify(P),beforeS=JSON.stringify(S);
      const save=localStorage.getItem('bf_global_offline_demo_v7');
      const values=()=>({
        level:document.getElementById('bf-nav-level').textContent,
        zel:document.getElementById('bf-nav-zel').textContent,
        karma:document.getElementById('bf-nav-karma').textContent,
        detail:document.getElementById('bf054-home-values').textContent
      });
      const result={};
      try {
        P.version=7;P.level=2;P.exp=4;P.zel=-3;P.karma='9';
        document.getElementById('plevel').textContent='99';
        document.getElementById('pzel').textContent='9,999';
        document.getElementById('pkarma').textContent='333';
        BF054HeaderStatus.refresh();
        result.invalid=values();
        BF_homeNav.go('quest');result.quest=values();
        BF_homeNav.go('home');result.home=values();
        // Claude blocker: a real second tap on Home while already Home
        // calls go('home') without bf-route-change; source text is stale.
        document.getElementById('pzel').textContent='500';
        document.querySelector('.bf-navbar button[data-bf-goto="home"]').click();
        result.sameRouteHome=values();
        P.level=2;P.exp=5;P.zel=1234;P.karma=9;
        BF054HeaderStatus.refresh();
        result.recovered=values();
        P.version=6;
        BF054HeaderStatus.refresh();
        result.invalidVersion=values();
      } finally {
        Object.assign(P,prev);
        for(const id of ids)
          document.getElementById(id).textContent=rendered[id];
        BF_homeNav.go('home');
        BF054HeaderStatus.refresh();
      }
      result.unchanged=JSON.stringify(P)===before &&
        JSON.stringify(S)===beforeS &&
        localStorage.getItem('bf_global_offline_demo_v7')===save;
      return result;
    }""")
    for kind in ('invalid','quest','home','sameRouteHome','invalidVersion'):
        item=header_probe[kind]
        assert (item['level'],item['zel'],item['karma'])==('—','—','—'),(kind,item)
        assert 'Lv./EXP unavailable' in item['detail'],(kind,item)
    recovered=header_probe['recovered']
    assert (recovered['level'],recovered['zel'],recovered['karma'])==(
        '2','1,234','9'),recovered
    assert 'Demo Lv.2' in recovered['detail'] and 'Zel 1,234' in recovered['detail']
    assert header_probe['unchanged'],header_probe
    page.set_viewport_size({'width':320,'height':844})
    status_bounds = details.evaluate("""el => {
      const b=el.getBoundingClientRect(), h=document.querySelector('.bf-shell-head').getBoundingClientRect();
      return {left:b.left,right:b.right,headerLeft:h.left,headerRight:h.right,viewport:innerWidth,
        documentWidth:document.documentElement.scrollWidth};
    }""")
    assert status_bounds['left'] >= -0.1 and status_bounds['right'] <= status_bounds['viewport'] + 0.1, status_bounds
    assert status_bounds['documentWidth'] <= max(status_bounds['viewport'], base_scroll_width), (status_bounds,base_scroll_width)
    # v615: owner screenshot rejected the v401 Quest-first narrow order.
    # The same real Home DOM must be title > OWNED portrait squad > story >
    # Adventure > optional preview > tools at every viewport width.
    # Keep redundant header detail after content, not before the portraits.
    before_priority=page.evaluate("""() => ({
      p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Object.keys(localStorage).sort().join(','),
      writes:__headerWrites()
    })""")
    page.wait_for_function("""() => {
      const h=document.getElementById('bf-home'),t=h?.querySelector('.bf-scene-title'),
        s=h?.querySelector('.bf-scene-squad');
      return t?.nextElementSibling===s;
    }""")
    assert page.evaluate("""() => {
      const h=document.getElementById('bf-home');
      return h.lastElementChild?.id==='bf054-home-details' &&
        h.querySelector('#bf-scene-party')?.children.length===6;
    }""")
    # Emulate #420 late-loading a read-only reference panel next to Adventure.
    page.evaluate("""() => {
      const adventure=document.querySelector('#bf-home .bf-scene-explore');
      const panel=document.createElement('section');
      panel.id='bf420-home-readiness';
      panel.setAttribute('aria-label','Late-loaded source preview fixture');
      panel.textContent='Reference preview, no save changes';
      adventure.after(panel);
    }""")
    capture_digests=[]
    for width in (320,360,370,371,390,412,540,320):
      page.set_viewport_size({'width':width,'height':844})
      layout=page.evaluate("""() => {
        const h=document.getElementById('bf-home'),
          t=h.querySelector('.bf-scene-title'),
          s=h.querySelector('.bf-scene-squad'),
          p=h.querySelector('#bf-scene-party'),
          story=h.querySelector('.bf-scene-story'),
          adventure=h.querySelector('.bf-scene-explore'),
          preview=h.querySelector('#bf420-home-readiness'),
          tools=h.querySelector('.bf-scene-tools'),
          details=h.querySelector('#bf054-home-details'),
          cards=[...p.querySelectorAll('.bf-scene-member')],
          rects=cards.map(x=>x.getBoundingClientRect()),
          buttons=[...adventure.querySelectorAll('button.bf-scene-active')];
        return {
          order:t.nextElementSibling===s&&s.nextElementSibling===story&&
            story.nextElementSibling===adventure&&
            adventure.nextElementSibling===preview&&
            preview.nextElementSibling===tools,
          detailsLast:h.lastElementChild===details,
          width:document.documentElement.scrollWidth,
          cols:getComputedStyle(p).gridTemplateColumns.split(' ').length,
          cards:cards.length,interactive:buttons.map(x=>x.dataset.bfGoto),
          firstRow:rects.slice(0,5).every(x=>Math.abs(x.top-rects[0].top)<2),
          sixthBelow:rects[5].top>=rects[0].bottom-2,
          hit:rects.every(x=>x.width>=36&&x.height>=44)
        };
      }""")
      assert layout['order'] and layout['detailsLast'],(width,layout)
      assert layout['cards']==6 and layout['interactive']==['quest','summon'],(width,layout)
      # v635: the original five-opening party frame (layout_home2.csv) is
      # used at every width; the sixth owned unit always sits below it.
      assert layout['cols']==5,(width,layout)
      assert layout['firstRow'] and layout['sixthBelow'],(width,layout)
      assert layout['hit'],(width,layout)
      assert layout['width']<=max(width,base_scroll_width),(width,layout)
      # In-memory Chromium image receipt; never publishes owner screenshots.
      page.evaluate("window.scrollTo(0,0)")
      import hashlib
      receipt=hashlib.sha256(page.screenshot()).hexdigest()
      assert len(receipt)==64
      capture_digests.append((width,receipt))
    assert len(capture_digests)==8
    # v615 Claude R2 mixed-slot mutation: the renderer always emits SIX
    # stable slot children, even when slot 2 has no owned unit. Slot 6 must
    # retain its dedicated compact row and original source ownership.
    page.set_viewport_size({'width':320,'height':844})
    mixed=page.evaluate("""() => {
      const old=P.squad.slice(), party=document.getElementById('bf-scene-party');
      const storageBefore=localStorage.getItem('bf_global_offline_demo_v7');
      try {
        if(old.length!==6||!old.every(id=>Number.isSafeInteger(id)&&P.roster.includes(id)))
          return {fixture:false,reason:'expected valid six-slot synthetic starter squad'};
        P.squad[1]=null; // disposable browser state only
        BFGlobalHome.refreshParty();
        const cards=[...party.children],last=cards[5],second=cards[1],
          css=getComputedStyle(last);
        const r0=cards[0].getBoundingClientRect(),
          r6=last.getBoundingClientRect();
        return {
          fixture:true,count:cards.length,
          secondEmpty:second.classList.contains('bf-scene-empty'),
          sixthButton:last.tagName==='BUTTON',
          sixthId:Number(last.dataset.bfHomeUnitId),
          expectedSixthId:old[5],
          compact:css.gridColumnStart==='1'&&css.gridColumnEnd==='-1',
          below:r6.top>=r0.bottom-2,
          saveSame:localStorage.getItem('bf_global_offline_demo_v7')===storageBefore
        };
      } finally {
        P.squad.splice(0,P.squad.length,...old);
        BFGlobalHome.refreshParty();
      }
    }""")
    assert mixed['fixture'] and mixed['count']==6 and mixed['secondEmpty'],mixed
    assert mixed['sixthButton'] and mixed['sixthId']==mixed['expectedSixthId'],mixed
    assert mixed['compact'] and mixed['below'] and mixed['saveSame'],mixed
    after_priority=page.evaluate("""() => ({
      p:JSON.stringify(P),s:JSON.stringify(S),quest:QUEST.missionId,
      save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Object.keys(localStorage).sort().join(','),
      writes:__headerWrites()
    })""")
    assert before_priority==after_priority,(before_priority,after_priority)
    page.evaluate("document.getElementById('bf420-home-readiness').remove()")
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate('()=>{P.exp=13;P.level=2;P.zel=1345;P.karma=250;renderProgress()}')
    page.wait_for_function("""()=>document.querySelector('#bf054-exp-text')?.textContent==='8 / 10'""")
    assert page.evaluate('Math.round(BF054HeaderStatus.state.percent)')==80
    assert page.locator('#bf054-exp').get_attribute('aria-valuemax')=='10'
    assert page.locator('#bf054-exp').get_attribute('aria-valuenow')=='8'
    assert page.locator('#bf-nav-level').inner_text()=='2'
    assert '1,345' in page.locator('#bf-nav-zel').inner_text()
    assert '250' in page.locator('#bf-nav-karma').inner_text()
    home_status=page.locator('#bf054-home-values').inner_text()
    assert 'Demo Lv.2' in home_status
    assert 'EXP 8/10' in home_status
    assert 'Zel 1,345' in home_status and 'Karma 250' in home_status
    assert 'Energy unavailable' in home_status
    assert page.locator('#bf054-home-next-level').inner_text()==(
        'Next demo level 3 · 2 EXP remaining · Total demo EXP 13.')
    page.locator('.bf-navbar button[data-bf-goto="quest"]').click()
    assert page.locator('#bf054-exp-text').inner_text()=='8 / 10'
    page.locator('.bf-navbar button[data-bf-goto="home"]').click()
    assert page.locator('#bf054-exp-text').inner_text()=='8 / 10'
    assert details.get_attribute('open') is not None
    page.evaluate('()=>{P.exp=0;P.level=1;P.zel=0;P.karma=0;renderProgress()}')
    page.wait_for_function("""()=>document.querySelector('#bf054-exp-text')?.textContent==='0 / 5'""")
    end=page.evaluate("""() => ({version:P.version,exp:P.exp,level:P.level,
        zel:P.zel,karma:P.karma,save:localStorage.getItem('bf_global_offline_demo_v7'),
        roster:JSON.stringify(P.roster),squad:JSON.stringify(P.squad)})""")
    assert end==initial,(initial,end)
    # Real native reward/level-up integration in this disposable page:
    # mission 1 earns 5 cumulative EXP and reaches demo level 2. The Home
    # readout must show the NEXT level's 10 EXP target, not reuse 5 or 0.
    page.evaluate('finish(true)')
    page.wait_for_function("""()=>document.querySelector('#bf054-home-next-level')
      ?.textContent==='Next demo level 3 · 10 EXP remaining · Total demo EXP 5.'""")
    assert page.evaluate('P.level')==2 and page.evaluate('P.exp')==5
    reward_state=page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
      quest:QUEST.missionId,raw:localStorage.getItem('bf_global_offline_demo_v7'),
      writes:__headerWrites()})""")
    for width in (320,390,540):
        page.set_viewport_size({'width':width,'height':844})
        page.evaluate('BF054HeaderStatus.refresh()')
        bounds=page.locator('#bf054-home-next-level').bounding_box()
        assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=width+1,(width,bounds)
    assert page.evaluate("""()=>({p:JSON.stringify(P),s:JSON.stringify(S),
      quest:QUEST.missionId,raw:localStorage.getItem('bf_global_offline_demo_v7'),
      writes:__headerWrites()})""")==reward_state
    assert not errors,errors
    browser.close()
print('PASS v0.54 native BF1 header crop, demo EXP live meter, unavailable Energy, v7 unchanged')
