function Cell(x, y){
    this._x = x;
    this._y = y;
}

function Droplet(id, source, target){
    this._id = id;
    this._source = source;
    this._target = target;
}

// 获得坐标中的x,y值，返回[x, y]
function get_x_y(position){
    x_y = position.substring(1, position.length-1).split(',');   
    return new Array(parseInt(x_y[0]), parseInt(x_y[1]));
}

function create_cell(position){
    x_y = get_x_y(position);   
    return new Cell(x_y[0], x_y[1]);
}

// 获得芯片的左下角坐标和右上角坐标
function get_dmfb_size(input_info){
    info = input_info.split('\n');
    var i;
    size = null;
    for (i = 0; i < info.length; i++) {
        if (info[i] == 'grid'){
            size_info = info[i+1].split(' ');
            size = {down_left: create_cell(size_info[0]), up_right: create_cell(size_info[1])};
            break;
        }
    }
    return size;
}

// 获得障碍数组
function get_dmfb_blockages(input_info){
    info = input_info.split('\n');
    var blockages = [];
    var i;
    for (i = 0; i < info.length; i++) {
        if (info[i] == 'blockages'){
            var j = i + 1;
            for (; j < info.length; j++){
                if (info[j] == 'end'){
                    break;
                }
            
                blocks = info[j].split(' ');
                
                up_left = get_x_y(blocks[0]);   
                down_right = get_x_y(blocks[1]);
                // temp = [];
                for (var x = up_left[0]; x <= down_right[0]; x++){
                    for (var y = up_left[1]; y >= down_right[1]; y--){
                        // temp.push(new cell(x, y));
                        blockages.push(new Cell(x, y));
                    }
                }  
                // blockages.push(temp); 
            }
            break;
        }
    }   
    return blockages;
}

// 获得液滴的起点和终点
function get_droplets_source_target(input_info){
    info = input_info.split('\n');
    var nets = [];
    for (var i = 0; i < info.length; i++){
        if (info[i] === 'nets'){
            var j = i + 1;
            for (; j < info.length; j++){
                if (info[j] === 'end'){
                    break;
                }
                droplet = info[j].split(' ');
                nets.push(new Droplet(parseInt(droplet[0]), create_cell(droplet[1]), create_cell(droplet[3])));
            }
            break;
        }
    }

    function sortDroplet(d1, d2){
        return d1._id - d2._id;
    }
    
    return nets.sort(sortDroplet);
}

// 获得液滴路径
function get_droplet_path(input_info){
    info = input_info.split('\n');
    var paths = [];
    for (var i = 0; i < info.length; i++){
        if (info[i] == 'routes'){
            var j = i + 1;
            for (; j < info.length; j++){
                if (info[j] == 'end'){
                    break;
                }
                route = info[j].split(' ');
                tmp = [];
                var k = 1;
                for(; k < route.length; k++){
                    tmp.push(create_cell(route[k]));
                }
                paths.push(tmp);
            }
            break;
        }
    }
    return paths;
}

// 统计路径信息
function get_paths_info(up_right_x, up_right_y,paths){
    let max_time_step = 0;
    let cell_used_num = 0;
    const board = [];
    for (var x = 0; x <= up_right_x; x++){
        var tmp = [];
        for (var y = 0; y <= up_right_y; y++){
            tmp.push(0);
        }
        board.push(tmp);
    }
    for (i in paths){
        var path = paths[i];
        if (path.length > max_time_step){
            max_time_step = path.length;
        }
        var k = 0;
        while (k < path.length){
            if (k != 0 && is_cell_eq(path[k], path[k-1]) == false){
                if (board[path[k]._x][path[k]._y] == 0){
                    board[path[k]._x][path[k]._y] += 1;
                    cell_used_num += 1;
                }
            }
            k += 1;
        }
    }
    return [max_time_step - 1, cell_used_num];
}

function get_droplet_pre_next_step(up_right_x, up_right_y, cell_length, paths, step){
    const next_steps = [];
    for (i in paths){
        var path = paths[i];
        var cur_cell = null;
        if (step >= path.length){
            cur_cell = path[path.length - 1];
        }else{
            cur_cell = path[step];
        }
        var next_x_y = change_x_y(up_right_x, up_right_y, cur_cell);
        next_steps.push([next_x_y[1] * cell_length, next_x_y[0] * cell_length]); // left, top
    }
    return next_steps;
}

function add_logs(element, step, info) {
    var print_log = "<p><br>#At &nbsp<span>" + step + "</span> step <br>";
    for (i in info){
        var msg = info[i];
        print_log += "=> droplet :d<sub>" + msg.id1 + "</sub>(<span>" + msg.pos1._x + "</span>, <span>" +
            msg.pos1._y + "</span>), d<sub>" + msg.id2 + "</sub>(<span>" + msg.pos2._x +
            "</span>, <span>" + msg.pos2._y + "</span>) <br> ==> violate <span>" + msg.type + "</span><br>";
    }
    print_log += "</p>";
    element.append(print_log);
}

function get_all_cur_interfere_area(up_right_x, up_right_y, info) {
    var areas = [];
    for (i in info){
        var msg = info[i];
        var pos1_area = get_interfere_area(up_right_x, up_right_y, msg.pos1);
        var pos2_area = get_interfere_area(up_right_x, up_right_y, msg.pos2);
        areas.push(pos1_area);
        areas.push(pos2_area);
    }
    return areas;
}

function show_interfere_area(up_right_x, up_right_y, areas) {
    for(i in areas){
        for (j in areas[i]){
            var c = areas[i][j];
            var index = get_cell_index(up_right_x, up_right_y, c);
            $(".cell:eq("+ index +") > div").css("background-color", "yellow");
        }
    }
}

function hide_interfere_area(up_right_x, up_right_y, areas) {
    for(i in areas){
        for (j in areas[i]){
            var c = areas[i][j];
            var index = get_cell_index(up_right_x, up_right_y, c);
            $(".cell:eq("+ index +") > div").css("background-color", "snow");
        }
    }
}

// 显示液滴的轨迹
// <img src="./images/up_arrow.png" alt="" width="" height="">
function show_droplet_trace(up_right_x, up_right_y, cell_length, path) {
    for(var i = 1; i < path.length - 1; i++){
        if(is_cell_eq(path[i], path[i - 1])){
            continue;
        }else{
            var dir = get_direction(path[i - 1], path[i]);
            var arrow_src;
            if (dir == 1){
                arrow_src = "../../static/mytool/images/left_arrow.png";
            }else if (dir == 2){
                arrow_src = "../../static/mytool/images/up_arrow.png";
            }else if (dir == 3){
                arrow_src = "../../static/mytool/images/right_arrow.png";
            }else{
                arrow_src = "../../static/mytool/images/down_arrow.png";
            }
            var cur_x_y = change_x_y(up_right_x, up_right_y, path[i]);
            var trace_img = "<div class='arrow' style='left:" + cur_x_y[1] * cell_length + "px; top:" + cur_x_y[0] * cell_length + "px;'>" + 
                "<img src=" + arrow_src + " width="+ cell_length +"px height=" + cell_length + "px>" +
                "</div>";
            $("#trace").append(trace_img);
            
        }
        $('.arrow').css({
            "width": cell_length + "px",
            "height": cell_length + "px"
        });
        // $('.droplet > div').css('display', "none");
        $('.droplet').css('opacity', 0.5);
    }
}



