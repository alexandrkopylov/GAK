var ref_time=60000;
var ref_functions=[]

var res_shed=setInterval(ref_timer_fun,ref_time);
function ref_timer_fun() {
    var tf=ref_functions.length;
    for (var i=0;i<tf;i++){
        var v=ref_functions[i]();
        
    }
}