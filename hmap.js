
(function(){const box=document.getElementById('hm');if(!box)return;let m=null,pts;
 function init(){if(m||innerWidth<900)return;
 m=L.map(box,{zoomControl:false,scrollWheelZoom:false,dragging:false,doubleClickZoom:false,boxZoom:false,keyboard:false,tap:false,attributionControl:false});
 L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',{maxNativeZoom:16,maxZoom:19}).addTo(m);
 const TG=[0,'15:00','A','B','C','D'];pts=P.map((p,i)=>p&&i!==3?[p[0],p[1],TG[i]]:null).filter(Boolean);
 pts.forEach(p=>L.marker([p[0],p[1]],{interactive:false,icon:L.divIcon({className:'hmp'+(p[2]==='15:00'?' meet':''),html:'<b>'+p[2]+'</b>',iconSize:[34,34],iconAnchor:[17,17]})}).addTo(m));
 m.fitBounds(L.latLngBounds(pts.map(p=>[p[0],p[1]])),{padding:[34,34]});
 }
 init();
 addEventListener('resize',()=>{if(!m){init();return}m.invalidateSize();m.fitBounds(L.latLngBounds(pts.map(p=>[p[0],p[1]])),{padding:[34,34]})});
})();
