var canvas = document.getElementById("cas");
var ctx = canvas.getContext("2d");
resize();
window.onresize = resize;
function resize() {
    canvas.width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    canvas.height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
}
var RAF = (function() {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(callback) {
        window.setTimeout(callback, 1000 / 60);
    };
})();
// got the coordinate of the mouse
var warea = { x: null, y: null, max: 20000 };
window.onmousemove = function(e) {
    e = e || window.event;
    warea.x = e.clientX;
    warea.y = e.clientY;
};
window.onmouseout = function(e) {
    warea.x = null;
    warea.y = null;
};
// add particles
// x, y are particle coordinates, xa, ya are particle xy axis acceleration, max is the maximum distance of the connection
var dots = [];
for(var i = 0; i < 70; i++) {
    var x = Math.random() * canvas.width;
    var y = Math.random() * canvas.height;
    var xa = Math.random() * 3 - 1;
    var ya = Math.random() * 3 - 1;
    dots.push({
        x: x,
        y: y,
        xa: xa,
        ya: ya,
        max: 16000
    })
}
// Delay the start of the animation for 100 seconds, if it is executed immediately, sometimes the position calculation will be wrong
setTimeout(function() {
    animate();
}, 100);
//The logic of each frame loop
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Add the mouse coordinates to generate a point array for comparing distance
    var ndots = [warea].concat(dots);
    dots.forEach(function(dot) {
        // 
        dot.x += dot.xa;
        dot.y += dot.ya;
        // Particle displacement
        dot.xa *= (dot.x > canvas.width || dot.x < 0) ? -1 : 1;
        dot.ya *= (dot.y > canvas.height || dot.y < 0) ? -1 : 1;
        // Draw points
        ctx.fillRect(dot.x - 0.5, dot.y - 0.5, 3, 3);
        ctx.fillStyle = "#fff";
        // Cyclically compare the distance between particles
        for(var i = 0; i < ndots.length; i++) {
            var d2 = ndots[i];
            if(dot === d2 || d2.x === null || d2.y === null) continue;
            var xc = dot.x - d2.x;
            var yc = dot.y - d2.y;
            // The distance between two particles
            var dis = xc * xc + yc * yc;
            // Distance ratio
            var ratio;
            // If the distance between two particles is less than the max value of the particle object, draw a line between the two particles
            if(dis < d2.max) {
                // If it is a mouse, let the particles move to the position of the mouse
                if(d2 === warea && dis > (d2.max / 2)) {
                    dot.x -= xc * 0.01;
                    dot.y -= yc * 0.01;
                }
                // Calculate the distance ratio
                ratio = (d2.max - dis) / d2.max;
                // Draw a line
                ctx.beginPath();
                ctx.lineWidth = ratio / 2;
                ctx.strokeStyle = 'rgba(255,255,255,' + (ratio + 0.2) + ')';
                ctx.moveTo(dot.x, dot.y);
                ctx.lineTo(d2.x, d2.y);
                ctx.stroke();
            }
        }
        // Delete the calculated particles from the array
        ndots.splice(ndots.indexOf(dot), 1);
    });
    RAF(animate);
}
