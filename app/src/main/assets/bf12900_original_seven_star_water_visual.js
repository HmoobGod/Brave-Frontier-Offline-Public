/* BF_GLOBAL_2022_SEVEN_STAR_WATER_VISUAL_PREVIEW_V12900 */
(() => {
  'use strict';
  // Source-pixel static CGG composition preview for 7★ Water form #20016.
  // PIL source-layer compositing is community-interpreted, NOT native 2022.
  // No combat, level, evolution, summon or save operations.
  if (window.BFGlobalOriginalSevenStarWaterVisualV12900) return;
  const source=Object.freeze({unitId:20016,originalRarity:7,
    originalCggFrames:23,frameWidth:480,frameHeight:400,columns:5,
    sourceAsset:'2022 original Global BF1 unit anime PNG/CGG/CGS',
    nativeBlendVerified:false,nativeTransformVerified:false,
    originalFramePlaybackVerified:false,playable:false,saveFieldsAdded:0});
  const path='content/seven_star_source_preview/unit_anime_atlas_20016.png';
  let promise=null;
  function getImage(){
    if(promise)return promise;
    promise=new Promise(resolve=>{
      const image=new Image();
      image.onload=()=>resolve(image.naturalWidth===2400&&image.naturalHeight===2000?image:null);
      image.onerror=()=>resolve(null);
      image.src=path;
    });
    return promise;
  }
  async function renderFrame(canvas,index,previewImage=null){
    if(!Number.isSafeInteger(index)||index<0||index>=source.originalCggFrames||
       !canvas||typeof canvas.getContext!=='function'||
       canvas.width!==240||canvas.height!==200)return false;
    const image=previewImage||await getImage();
    if(!image||image.naturalWidth!==2400||image.naturalHeight!==2000)return false;
    const ctx=canvas.getContext('2d',{alpha:true});
    if(!ctx)return false;
    ctx.clearRect(0,0,240,200);
    ctx.imageSmoothingEnabled=false;
    ctx.drawImage(image,(index%5)*480,Math.floor(index/5)*400,480,400,0,0,240,200);
    return true;
  }
  window.BFGlobalOriginalSevenStarWaterVisualV12900=Object.freeze({source,path,renderFrame});
})();
