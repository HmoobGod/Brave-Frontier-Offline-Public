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
assert 'Number.isSafeInteger(P.level)' in addon and 'Number.isSafeInteger(P.exp)' in addon
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
      const saved={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>saved[k]??null,setItem:(k,v)=>{saved[k]=String(v)},
        removeItem:k=>{delete saved[k]},key:i=>Object.keys(saved)[i]??null,
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
          home:document.getElementById('bf054-home-values').textContent};
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
      }finally{
        P.level=oldLevel;P.exp=oldExp;P.version=oldVersion;
        BF054HeaderStatus.refresh();
      }
      result.saveUnchanged=localStorage.getItem('bf_global_offline_demo_v7')===save;
      result.normal=BF054HeaderStatus.state.valid;
      return result;
    }""")
    for kind in ('zeroLevel','stringLevel','outOfRangeLevel','negativeExp',
                 'nanExp','infiniteExp','stringExp','invalidVersion'):
        item=invalid[kind]
        assert item['state']['valid'] is False,(kind,item)
        assert item['text']=='— / —',(kind,item)
        assert 'unavailable' in item['aria'],(kind,item)
        assert 'Lv./EXP unavailable' in item['home'],(kind,item)
    assert invalid['saveUnchanged'] and invalid['normal'],invalid
    page.set_viewport_size({'width':320,'height':844})
    status_bounds = details.evaluate("""el => {
      const b=el.getBoundingClientRect(), h=document.querySelector('.bf-shell-head').getBoundingClientRect();
      return {left:b.left,right:b.right,headerLeft:h.left,headerRight:h.right,viewport:innerWidth,
        documentWidth:document.documentElement.scrollWidth};
    }""")
    assert status_bounds['left'] >= -0.1 and status_bounds['right'] <= status_bounds['viewport'] + 0.1, status_bounds
    assert status_bounds['documentWidth'] <= max(status_bounds['viewport'], base_scroll_width), (status_bounds,base_scroll_width)
    # v401: narrow Home physically reorders existing source-art Quest/Summon
    # tiles above the optional squad/status stack, never clones links or
    # changes keyboard versus visual order. Responsive return restores DOM.
    page.wait_for_function("""() => {
      const e=document.querySelector('#bf-home .bf-scene-explore');
      return e?.nextElementSibling?.classList.contains('bf-scene-squad');
    }""")
    layout=page.evaluate("""() => {
      const home=document.getElementById('bf-home');
      const adventure=home.querySelector('.bf-scene-explore');
      const squad=home.querySelector('.bf-scene-squad');
      const tiles=[...adventure.querySelectorAll('button.bf-scene-active')];
      const bar=document.querySelector('.bf-navbar').getBoundingClientRect();
      return {first:home.contains(adventure)&&adventure.nextElementSibling===squad,
        tileCount:tiles.length,
        tileBottom:Math.max(...tiles.map(b=>b.getBoundingClientRect().bottom)),
        navTop:bar.top,
        noOverflow:document.documentElement.scrollWidth<=innerWidth};
    }""")
    assert layout['first'] and layout['tileCount']==2,layout
    assert layout['tileBottom'] < layout['navTop'],layout
    assert layout['noOverflow'],layout
    # Future Home squad metadata from separately reviewed patches must not
    # push the two actual playable locations below the first phone screen.
    extra=page.evaluate("""() => {
      const e=document.querySelector('#bf-home .bf-scene-squad');
      for(let i=0;i<4;i++){
        const n=document.createElement('p');n.className='bf401-test-metadata';
        n.textContent='Supplemental source-backed Home status '+i;
        n.style.height='48px';e.append(n);
      }
      return document.querySelector('.bf-scene-explore button.bf-scene-active')
        .getBoundingClientRect().top;
    }""")
    assert extra < layout['navTop'],(extra,layout)
    page.evaluate("""() => document.querySelectorAll('.bf401-test-metadata')
      .forEach(e=>e.remove())""")
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_function("""() => {
      const e=document.querySelector('#bf-home .bf-scene-explore');
      return e?.nextElementSibling?.classList.contains('bf-scene-tools');
    }""")
    assert page.evaluate("""() => {
      const h=document.getElementById('bf-home'),e=h.querySelector('.bf-scene-explore');
      return e.previousElementSibling.classList.contains('bf-scene-story')&&
        document.documentElement.scrollWidth<=innerWidth;
    }""")
    page.set_viewport_size({'width':540,'height':844})
    assert page.evaluate("""() => document.querySelector('.bf-scene-explore')
      .nextElementSibling.classList.contains('bf-scene-tools')""")
    # v401 R2: emulate the late-loaded #420 optional panel that follows
    # Adventure in the latest main. The old branch predates the actual v420
    # asset; verify DOM adjacency and no duplicate controls on every resize.
    before_reorder=page.evaluate("""() => ({
      p:JSON.stringify(P),quest:QUEST.missionId,
      auto:S.auto,save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Object.keys(localStorage).sort().join(',')
    })""")
    page.evaluate("""() => {
      const adventure=document.querySelector('#bf-home .bf-scene-explore');
      const panel=document.createElement('section');
      panel.id='bf420-home-readiness';
      panel.setAttribute('aria-label','Late-loaded source preview fixture');
      panel.textContent='2022 reference preview, no save changes';
      adventure.after(panel);
    }""")
    for width in (320,390,370,371,540,320):
      page.set_viewport_size({'width':width,'height':844})
      page.wait_for_function("""() => {
        const e=document.querySelector('#bf-home .bf-scene-explore'),
              p=document.getElementById('bf420-home-readiness'),
              squad=document.querySelector('#bf-home .bf-scene-squad'),
              tools=document.querySelector('#bf-home .bf-scene-tools');
        if(!e||!p||e.nextElementSibling!==p)return false;
        return innerWidth<=370?p.nextElementSibling===squad:
          p.nextElementSibling===tools;
      }""")
      structure=page.evaluate("""() => {
        const home=document.getElementById('bf-home'),
              adventure=home.querySelector('.bf-scene-explore'),
              panel=home.querySelector('#bf420-home-readiness'),
              squad=home.querySelector('.bf-scene-squad'),
              story=home.querySelector('.bf-scene-story'),
              tools=home.querySelector('.bf-scene-tools'),
              buttons=[...home.querySelectorAll('.bf-scene-explore button.bf-scene-active')];
        return {
          sameParent:adventure.parentElement===story.parentElement,
          adjacent:adventure.nextElementSibling===panel,
          first:innerWidth<=370?panel.nextElementSibling===squad:
            story.nextElementSibling===adventure,
          next:innerWidth<=370?panel.nextElementSibling===squad:
            panel.nextElementSibling===tools,
          tiles:buttons.map(b=>b.dataset.bfGoto),
          panelCount:home.querySelectorAll('#bf420-home-readiness').length,
          scroll:document.documentElement.scrollWidth,viewport:innerWidth
        };
      }""")
      assert structure['sameParent'] and structure['adjacent'],(width,structure)
      assert structure['first'] and structure['next'],(width,structure)
      assert structure['tiles']==['quest','summon'] and structure['panelCount']==1,(width,structure)
      assert structure['scroll']<=max(width,base_scroll_width),(width,structure)
    after_reorder=page.evaluate("""() => ({
      p:JSON.stringify(P),quest:QUEST.missionId,
      auto:S.auto,save:localStorage.getItem('bf_global_offline_demo_v7'),
      keys:Object.keys(localStorage).sort().join(',')
    })""")
    assert before_reorder==after_reorder,(before_reorder,after_reorder)
    page.evaluate("document.getElementById('bf420-home-readiness').remove()")
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_function("""() => {
      const e=document.querySelector('#bf-home .bf-scene-explore');
      return e?.nextElementSibling?.classList.contains('bf-scene-tools');
    }""")
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
    assert not errors,errors
    browser.close()
print('PASS v0.54 native BF1 header crop, demo EXP live meter, unavailable Energy, v7 unchanged')
