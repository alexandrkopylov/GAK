var PillarMarker=L.Marker.extend(
      {
        prevPillar: null,
        nextPillar: null,
        num_by_vl: null,
        visPillarAttr: null,
        pillarTap: null,
        map: null,
        inputLine: null,
        outputLine: null,
        parentLine: null,
        tapsLine: null,
        pillarType: -1,
        pillarCut: -1,
        pillarMaterial: -1,
        
        onMouseDown: function(event)
        {
          this.visPillarAttr.SelectPillar(this);
        },
        
        onMove: function(event)
        {
          if ((!this.options.isBase) && (!this.noMove))
          {
            var latPrevPillar=this.prevPillar.getLatLng().lat;
            var lngPrevPillar=this.prevPillar.getLatLng().lng;
            var latNextPillar=this.nextPillar.getLatLng().lat;
            var lngNextPillar=this.nextPillar.getLatLng().lng;
            var newDistance=this.prevPillar.getLatLng().distanceTo(event.latlng);
            var fullDistance=this.prevPillar.getLatLng().distanceTo(this.nextPillar.getLatLng());
            var k=newDistance/fullDistance;
            if (k>0.9999) k=0.9999;
            var newLat=latPrevPillar+(latNextPillar-latPrevPillar)*k;
            var newLng=lngPrevPillar+(lngNextPillar-lngPrevPillar)*k;
            this.noMove=true;
            this.setLatLng(L.latLng(newLat, newLng));
          }
          if (this.noMove)
          {
            this.noMove=false;
          }
          if (this.inputLine)
          {
            this.inputLine.setNewEndCoord(this.getLatLng());
          }
          if (this.outputLine)
          {
            this.outputLine.setNewStartCoord(this.getLatLng());
          }
          for (var i in this.tapsLine)
          {
            this.tapsLine[i].setNewStartCoord(this.getLatLng());
          }
          this.visPillarAttr.UpdateCoord();
        },
        
        initialize: function(latlng, options, map, visPillarAttr)
        {
          this.setLatLng(latlng);
          L.setOptions(this, options);
          this.on('mousedown',this.onMouseDown);
          this.on('move',this.onMove);
          this.visPillarAttr=visPillarAttr;
          this.map=map;
          this.tapsLine=[];
        },
        
        setPillarTap: function(TAP)
        {
          this.pillarTap=TAP;
          TAP.addPillar(this);
          if (this.inputLine)
          {
            this.inputLine.setLineTap(TAP);
          }
        },
        
        addToForward: function(forwardPillar)
        {
          forwardPillar.setPillarTap(this.pillarTap);
          if (!this.outputLine)
          {
            var aplLine=new AplLine([this.getLatLng(),forwardPillar.getLatLng()],this.map,this,forwardPillar);
            this.outputLine=aplLine;
            forwardPillar.inputLine=aplLine;
            this.nextPillar=forwardPillar;
            forwardPillar.prevPillar=this;
          }
          else
          {
            var oldEndPillar=this.outputLine.endPillar;
            this.outputLine.remove();
            this.outputLine=null;
            this.addToForward(forwardPillar);
            forwardPillar.addToForward(oldEndPillar);
            this.pillarTap.sortPillar(null);
          }
        },
        
        addToBack: function(backPillar)
        {
          backPillar.setPillarTap(this.pillarTap);
          if (!this.inputLine)
          {
            backPillar.addToForward(this);
            this.pillarTap.sortPillar(backPillar);
          }
          else
          {
            this.inputLine.startPillar.addToForward(backPillar);
          }
        },
        
        addToBetween: function(pillar, nextPillar)
        {
          pillar.nextPillar=nextPillar;
          pillar.prevPillar=this;
          nextPillar.prevPillar=pillar;
          pillar.visPillarAttr=this.visPillarAttr;
          pillar.setPillarTap(nextPillar.pillarTap);
          if (this.pillarTap==nextPillar.pillarTap)
          {
            this.nextPillar=pillar;
            this.pillarTap.sortPillar(null);
          }
          else
          {
            pillar.pillarTap.sortPillar(pillar);
          }
        },
        
        addToTap: function(pillar)
        {
          var aplLine=new AplLine([this.getLatLng(),pillar.getLatLng()],this.map,this,pillar);
          pillar.inputLine=aplLine
          aplLine.setLineTap(pillar.pillarTap);
          this.tapsLine.push(aplLine);
        },
        
        setInputLine: function(aplLine)
        {
          this.inputLine=aplLine;
        },
        
        setOutputLine: function(aplLine)
        {
          this.outputLine=aplLine;
        },
        
        setNextPillar: function(pillar)
        {
          this.nextPillar=pillar;
        },
        
        setPrevPillar: function(pillar)
        {
          this.prevPillar=pillar;
        },
        
        setNumByVL: function(num_by_vl)
        {
          this.num_by_vl=num_by_vl;
          this.setPillarIcon(null);
        },
        
        setPillarIcon: function(actFillColor)
        {
          if (!this.pillarTap) return;
          var fillColor='#0000FF';
          var strokeColor='#0000FF';
          var contourColor='True';
          var strokeThick=1;
          for (var i of PillarMarker.PillarIconMap.keys())
          {
              if (PillarMarker.PillarIconMap.get(i).pillarType==this.pillarType && PillarMarker.PillarIconMap.get(i).pillarCut==this.pillarCut)
              {
                  if  (PillarMarker.PillarIconMap.get(i).fillColor) fillColor=PillarMarker.PillarIconMap.get(i).fillColor;
                  if  (PillarMarker.PillarIconMap.get(i).strokeColor) strokeColor=PillarMarker.PillarIconMap.get(i).strokeColor;
                  if  (PillarMarker.PillarIconMap.get(i).strokeThick) strokeThick=PillarMarker.PillarIconMap.get(i).strokeThick;
                  if  (PillarMarker.PillarIconMap.get(i).contourColor) contourColor=PillarMarker.PillarIconMap.get(i).contourColor;
                  if (contourColor=='False') fillColor='none';
                  if (actFillColor) fillColor=actFillColor;
                  var pillarIcon=new L.divIcon({html: '<svg width="30" height="30"><path fill="'+fillColor+'" stroke="'+strokeColor+'" stroke-width="'+strokeThick+'" d="'+PillarMarker.PillarIconMap.get(i).svg+'" transform="translate(5,5)"/><foreignObject class="node" width="30" height="15" x="15" y="15"><div style="color:'+strokeColor+'">'+this.num_by_vl+'</div></foreignObject></svg>', className: 'markerClass', iconAnchor: [10,10]});
                  this.setIcon(pillarIcon);
                  return;
              }
          }
          for (var i of PillarMarker.PillarIconMap.keys())
          {
              if (PillarMarker.PillarIconMap.get(i).pillarType==this.pillarType && PillarMarker.PillarIconMap.get(i).pillarCut==-1)
              {
                  if  (PillarMarker.PillarIconMap.get(i).fillColor) fillColor=PillarMarker.PillarIconMap.get(i).fillColor;
                  if  (PillarMarker.PillarIconMap.get(i).strokeColor) strokeColor=PillarMarker.PillarIconMap.get(i).strokeColor;
                  if  (PillarMarker.PillarIconMap.get(i).strokeThick) strokeThick=PillarMarker.PillarIconMap.get(i).strokeThick;
                  if  (PillarMarker.PillarIconMap.get(i).contourColor) contourColor=PillarMarker.PillarIconMap.get(i).contourColor;
                  if (contourColor=='False') fillColor='none';
                  if (actFillColor) fillColor=actFillColor;
                  var pillarIcon=new L.divIcon({html: '<svg width="30" height="30"><path fill="'+fillColor+'" stroke="'+strokeColor+'" stroke-width="'+strokeThick+'" d="'+PillarMarker.PillarIconMap.get(i).svg+'" transform="translate(5,5)"/><foreignObject class="node" width="30" height="15" x="15" y="15"><div style="color:'+strokeColor+'">'+this.num_by_vl+'</div></foreignObject></svg>', className: 'markerClass', iconAnchor: [10,10]});
                  this.setIcon(pillarIcon);
                  return;
              }
          }
          i="2";
          if  (PillarMarker.PillarIconMap.get(i).fillColor) fillColor=PillarMarker.PillarIconMap.get(i).fillColor;
          if  (PillarMarker.PillarIconMap.get(i).strokeColor) strokeColor=PillarMarker.PillarIconMap.get(i).strokeColor;
          if  (PillarMarker.PillarIconMap.get(i).strokeThick) strokeThick=PillarMarker.PillarIconMap.get(i).strokeThick;
          if  (PillarMarker.PillarIconMap.get(i).contourColor) contourColor=PillarMarker.PillarIconMap.get(i).contourColor;
          if (contourColor=='False') fillColor='none';
          if (actFillColor) fillColor=actFillColor;
          var pillarIcon=new L.divIcon({html: '<svg width="30" height="30"><path fill="'+fillColor+'" stroke="'+strokeColor+'" stroke-width="'+strokeThick+'" d="'+PillarMarker.PillarIconMap.get(i).svg+'" transform="translate(5,5)"/><foreignObject class="node" width="30" height="15" x="15" y="15"><div style="color:'+strokeColor+'">'+this.num_by_vl+'</div></foreignObject></svg>', className: 'markerClass', iconAnchor: [10,10]});
          this.setIcon(pillarIcon);
        },
        
        setParentLine: function(parentLine)
        {
          this.parentLine=parentLine;
        },
        
        setPillarType: function(pillarType)
        {
          this.pillarType=pillarType;
        },
        
        setPillarCut: function(pillarCut)
        {
          this.pillarCut=pillarCut;
        },
        
        setPillarMaterial: function(pillarMaterial)
        {
          this.pillarMaterial=pillarMaterial;
        },
        
        remove: function()
        {
          this.visPillarAttr.HidePillarControl();
          this.map.removeLayer(this);
          if (this.inputLine && this.outputLine)
          {
            var startPillar=this.inputLine.startPillar;
            var endPillar=this.outputLine.endPillar;
            if (startPillar.pillarTap==this.pillarTap)
            {
              startPillar.outputLine=null
              endPillar.inputLine=null;
              startPillar.addToForward(endPillar);
              startPillar.outputLine.transferPillarFromLines(this.inputLine,this.outputLine);
              this.inputLine.remove();
              this.outputLine.remove();
              this.pillarTap.sortPillar(null);
            }
            else
            {
              ///Отпайка///
              var removeLineIndex=startPillar.tapsLine.indexOf(this.inputLine);
              if (removeLineIndex) startPillar.tapsLine.splice(removeLineIndex, 1);
              this.inputLine.remove();
              this.outputLine.remove();
              startPillar.addToTap(endPillar);
              endPillar.pillarTap.sortPillar(endPillar);
            }
          }
          else
          {
            if (this.inputLine)
            {
              var startPillar=this.inputLine.startPillar;
              if (startPillar.pillarTap==this.pillarTap)
              {
                startPillar.outputLine=null;
                startPillar.nextPillar=null;
                this.inputLine.remove();
                this.pillarTap.sortPillar(null);
              }
              else
              {
                //отпайка
                var removeLineIndex=startPillar.tapsLine.indexOf(this.inputLine);
                if (removeLineIndex) startPillar.tapsLine.splice(removeLineIndex, 1);
                this.inputLine.remove();
                this.inputLine=null;
                this.pillarTap.remove();
              }
            }
            else
            {
              if (this.outputLine)
              {
                var endPillar=this.outputLine.endPillar;
                endPillar.inputLine=null;
                endPillar.prevPillar=null;
                this.outputLine.remove();
                this.pillarTap.sortPillar(endPillar);
              }
              else
              {
                if (this.prevPillar)
                {
                  this.prevPillar.nextPillar=this.nextPillar;
                }
                if (this.nextPillar)
                {
                  this.nextPillar.prevPillar=this.prevPillar;
                }
                if (!this.prevPillar || !this.nextPillar) this.pillarTap.remove();
                this.pillarTap.sortPillar(null);
              }
            }
          }
          for (var i in this.tapsLine)
          {
            this.tapsLine[i].endPillar.pillarTap.remove();
          }
          if (this.parentLine)
          {
            this.parentLine.removePillar(this);
          }
        },
        
        getJSON()
        {
          var JSON={};
          JSON.id=this.pillarTap.id+"_"+this.num_by_vl;
          if (this.prevPillar) JSON.prevPillar=this.prevPillar.pillarTap.id+"_"+this.prevPillar.num_by_vl;
          if (this.nextPillar) JSON.nextPillar=this.nextPillar.pillarTap.id+"_"+this.nextPillar.num_by_vl;
          if (this.inputLine) JSON.inputLine=this.inputLine.startPillar.pillarTap.id+"_"+this.inputLine.startPillar.num_by_vl;
          if (this.parentLine) JSON.parentLine=this.parentLine.startPillar.pillarTap.id+"_"+this.parentLine.startPillar.num_by_vl+"_"+this.parentLine.endPillar.pillarTap.id+"_"+this.parentLine.endPillar.num_by_vl;
          if (this.tapsLine.length>0)
          {
            var tapsLine=[];
            for (var i in this.tapsLine)
            {
              tapsLine.push(this.tapsLine[i].endPillar.pillarTap.id+"_"+this.tapsLine[i].endPillar.num_by_vl);
            }
            JSON.tapsLine=tapsLine;
          }
          JSON.pillarType=this.pillarType;
          JSON.pillarCut=this.pillarCut;
          JSON.pillarMaterial=this.pillarMaterial;
          JSON.pillarLatitude=this.getLatLng().lat;
          JSON.pillarLongitude=this.getLatLng().lng;
          return JSON;
        },
        
        toBase()
        {
          this.options.isBase=true;
          
          var nextBasePillar=this.parentLine.endPillar;
          var aplLine=new AplLine([this.getLatLng(),nextBasePillar.getLatLng()],this.map,this,nextBasePillar);
          this.outputLine=aplLine;
          nextBasePillar.inputLine=aplLine;
          var nextPillar=this.nextPillar;
          while(!nextPillar.options.isBase)
          {
            nextPillar.parentLine=aplLine;
            aplLine.PillarArray.push(nextPillar);
            nextPillar=nextPillar.nextPillar;
          }
          
          var prevBasePillar=this.parentLine.startPillar;
          aplLine=new AplLine([prevBasePillar.getLatLng(),this.getLatLng()],this.map,prevBasePillar,this);
          this.inputLine=aplLine;
          if (this.pillarTap==prevBasePillar.pillarTap)
          {
            prevBasePillar.outputLine=aplLine;
          }
          else
          {
            var removeLineIndex=prevBasePillar.tapsLine.indexOf(this.parentLine);
            if (removeLineIndex) prevBasePillar.tapsLine.splice(removeLineIndex, 1);
            prevBasePillar.tapsLine.push(aplLine);
          }
          var prevPillar=this.prevPillar;
          while(!prevPillar.options.isBase)
          {
            prevPillar.parentLine=aplLine;
            aplLine.PillarArray.push(prevPillar);
            prevPillar=prevPillar.prevPillar;
          }
          this.parentLine.PillarArray=[];
          this.parentLine.remove();
          this.parentLine=null;
        },
        
      });