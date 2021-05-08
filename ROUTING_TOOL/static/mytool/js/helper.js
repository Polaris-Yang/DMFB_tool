// 返回网格单元的序号，从左到右，从上到下
function get_cell_index(up_right_x, up_right_y, cell){
    var col = cell._x;
    var row = up_right_y - cell._y;
    var index = row * up_right_x + col - 1;  
    return index;
}

droplet_colors = [
    "#FF0000",
    "#0000FF",
    "#FF7F24",
    "#C71585",
    "#FF00FF",
    "#FFD700",
    "#CDCD00",
    "#8470FF",
    "#3A5FCD",
    "#CAFF70",
    "#5CACEE",
    "#71C671"
];

// 原点在左上角，x为行，y为列
function change_x_y(up_right_x, up_right_y, cell){
    var y = cell._x - 1;
    var x = up_right_y - cell._y;
    return [x, y];
}

function is_cell_eq(c1, c2){
    return c1._x == c2._x && c1._y == c2._y;
}

function is_interfere(c1, c2){
    return Math.abs(c1._x - c2._x) <= 1 && Math.abs(c1._y - c2._y) <= 1;
}

// 获得液滴周围的干扰区
function get_interfere_area(up_right_x, up_right_y, cell){
    var interfere_area = [];
    for(var x = cell._x - 1; x <= cell._x + 1; x++){
        for(var y = cell._y - 1; y <= cell._y + 1; y++){
            if (x >= 1 && x <= up_right_x && y >= 1 && y <= up_right_y){
                var c = new Cell(x, y);
                var index = get_cell_index(up_right_x, up_right_y, c);
                if ($(".cell:eq("+ index +") > div").hasClass("blockage") == false){
                    interfere_area.push(c);
                }
            }
        }
    }
    return interfere_area;
}

// 获得当前时刻所有液滴的位置
function get_droplets_cur_cell(paths, step){
    const cur_cells = [];
    for (let i in paths){
        const path = paths[i];
        let cur_cell = null;
        if (step >= path.length){
            cur_cell = path[path.length - 1];
        }else{
            cur_cell = path[step];
        }
        cur_cells.push(cur_cell);
    }
    return cur_cells;
}

function check_droplets_interfere(droplets, paths, cur_step, max_time_step) {

    const cur_cells = get_droplets_cur_cell(paths, cur_step);
    let next_cells = [];
    // if (cur_step + 1 <= max_time_step){
    //     next_cells = get_droplets_cur_cell(paths, cur_step + 1);
    // }
    next_cells = get_droplets_cur_cell(paths, cur_step - 1);

    const interfere_info = [];
    for (let i = 0; i < cur_cells.length; i++){
        // 同一个液滴前后网格不连续或者直接走对角线
        if (is_interfere(cur_cells[i], next_cells[i]) === false || (Math.abs(cur_cells[i]._x - next_cells[i]._x) === 1 && Math.abs(cur_cells[i]._y - next_cells[i]._y) == 1)){
            interfere_info.push({
                id1: i + 1,
                pos1: cur_cells[i],
                id2: i + 1,
                pos2: next_cells[i],
                type : "Path continuous"
            });
        }
        let cur_target = droplets[i]._target;
        for(let j = i + 1; j < cur_cells.length; j++){
            let other_target = droplets[j]._target;
            let static_con = false;
            if (is_interfere(cur_cells[i], cur_cells[j]) && is_cell_eq(cur_target, other_target) === false){ // 违背静态约束
                interfere_info.push({
                    id1: i + 1,
                    pos1: cur_cells[i],
                    id2: j + 1,
                    pos2: cur_cells[j],
                    type : "static constraint"
                });
                static_con = true;
            }
            // 违背动态约束
            if (next_cells.length !== 0 && static_con === false && is_cell_eq(cur_target, other_target) === false){
                if (is_interfere(cur_cells[i], next_cells[j]) || is_interfere(cur_cells[j], next_cells[i])){
                    interfere_info.push({
                        id1: i + 1,
                        pos1: cur_cells[i],
                        id2: j + 1,
                        pos2: cur_cells[j],
                        type : "dynamic constraint"
                    });
                }
            }

            if (is_cell_eq(cur_target, other_target)){
                if (is_interfere(cur_cells[i], cur_cells[j]) || (next_cells.length !== 0
                    && is_interfere(cur_cells[i], next_cells[j]) || is_interfere(cur_cells[j], next_cells[i]))){
                    interfere_info.push({
                        id1: i + 1,
                        pos1: cur_cells[i],
                        id2: j + 1,
                        pos2: cur_cells[j],
                        type : "droplet mixing"
                    });
                }
            }
        }
    }

    if (cur_step === 18){
        console.log(interfere_info);
    }
    return interfere_info;
}

// c1为路径的上一个网格，c2为当前的网格
// 返回c2位于c1的哪个方位，左上右下===》1,2,3,4
function get_direction(c1, c2) {
    if(c2._x < c1._x){
        return 1;
    }else if (c2._y > c1._y){
        return 2;
    }else if (c2._x > c1._x){
        return 3;
    }else{
        return 4;
    }
}

function change_pos_for_infsci18(){
    var index_for_col_row = [];
    var i = 0;
    var j = 0;
    // 第一行
    for(j = 0; j < 12; j++){
        index_for_col_row.push([0, j]);
    }
    // 第2，3行
    var col1 = [0,4,5,6,7,8,9,10,11];
    for (i = 1; i <=2; i++){
        for(j = 0; j < col1.length; j++){
            index_for_col_row.push([i, col1[j]]);
        }
    }
    // 第4行
    for(j = 0; j < 12; j++){
        index_for_col_row.push([3, j]);
    }
    // 第5行
    var col2 = [0,1,2,3,4,5,6,7,10,11];
    for(j = 0; j < col2.length; j++){
        index_for_col_row.push([4, col2[j]]);
    }
    // 第6行
    var col3 = [0,4,5,6,7,10,11];
    for(j = 0; j < col3.length; j++){
        index_for_col_row.push([5, col3[j]]);
    }
    // 第7,8行
    for (i = 6; i <=7; i++){
        for(j = 0; j < col1.length; j++){
            index_for_col_row.push([i, col1[j]]);
        }
    }
    // 第9,10,11行
    for (i = 8; i <=10; i++){
        for(j = 0; j < col2.length; j++){
            index_for_col_row.push([i, col2[j]]);
        }
    }
    // 第12行
    for(j = 0; j < 12; j++){
        index_for_col_row.push([11, j]);
    }
    return index_for_col_row;
}
// infsci18 text2_1
// var d_path = [118, 117, 116, 115, 114, 104, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 94, 84, 72, 63, 64, 65, 66, 57, 50];
//var d_path = [107,97,87,77,78,79,79,79,79,79,79,80,80,80,81,69,70,71,72,63,56,56,49,37,36,24,15,24,23,22,13, 22];
// var d_path = [96, 96, 96, 95, 105, 117, 116, 115, 114, 113];
// var d_path = [0, 12, 12, 21, 30, 31, 32, 33, 33, 33, 34, 22, 13, 14, 15, 16, 17, 18, 19, 28, 40, 50, 57, 66, 75, 85, 95, 105];
// var d_path = [109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 109, 108, 107, 107, 97, 87,77, 78, 79, 80, 81, 69, 70, 71, 72, 84, 94];
// var d_path = [2,3,4,13,14,23,23,23,23,24,24,24,36,36,36,36,36,24,15,6,5,4,3,2,1,0,12,21,30,42,52,59,68,77,
//     78, 79, 89];
// var d_path = [76, 75, 66, 65, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 63, 56, 55, 54];
//var d_path = [111, 101, 91, 81, 69, 69, 69, 69, 69, 69, 70, 71, 62, 55, 54, 53, 46, 45, 33, 32];
//var d_path = [59,59,59,59,59,59,59,59,68,77,77,77,77,77,77,77,77,78,79,80,81,81,69,70,70,70,71,72,63,64,65];
// var d_path = [30,31,32,33,45,46,47,47,54,54,53,53,46,34,34,22,13,4,3,2,1,0,12,21,30,42,52,59,68,77,78,79,
//     80, 81, 69, 70, 71];
// var d_path = [51,51,51,51,51,51,51,51,51,51,51,51,51,50,40,39,39,38,38,37,36,24,15,14,13,4,3,2,1,0,12,21];
var d_path = [20,19,18,17,16,7,6,5,4,3,2,1,0,12,21,30,42,52,59,68,77,78,79,89,90,91,101];

// infsci18 text2_2
// var d1_path = [118, 117, 116, 115, 114, 113, 103, 93, 93, 93, 93, 92, 91, 81, 69, 70, 71, 72, 73, 74, 65, 66, 57, 50];
// var d_path = [107, 97, 97, 97, 98, 99, 100, 101, 91, 81, 69, 60, 53, 54, 55, 56, 49, 37, 36, 35, 34, 22];
// var d_path = [96, 96, 95, 95, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 105, 117, 116, 115, 115, 114, 113];
// var d_path = [0,12,21,21,30,42,43,44,44,44,44,44,43,42,52,59,68,77,87,88,89,79,80,81,69,70,71,72,73,74,75,
//     85, 95, 105];
// var d_path = [109, 99, 89, 79, 79, 79, 79, 79, 79, 79, 79, 79, 79, 79, 89, 99, 100, 101, 91, 92, 93, 94];
// var d_path = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,0,12,21,30,42,52,59,68,68,77,87,88,89];
// var d_path = [76, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 75, 66, 57, 50, 40, 39, 38, 37, 49, 56, 55, 54];
//var d_path = [111, 101, 91, 81, 69, 60, 60, 60, 60, 53, 46, 34, 34, 33, 32];
// var d_path = [59,59,59,59,59,59,59,59,52,42,30,21,21,21,21,30,42,52,59,68,68,77,87,88,89,79,80,81,69,70,71,
//     72, 73, 74, 65];
// var d_path = [30,42,43,44,32,33,34,34,34,22,13,14,15,15,15,15,15,15,16,17,17,17,17,17,17,26,38,37,49,49,49,
//     49, 49, 56, 63, 72, 71];
// var d_path = [51,51,51,50,50,40,40,40,39,38,37,36,36,36,35,34,22,13,4,3,2,1,0,12,21];
//var d_path = [20, 19, 18, 17, 26, 38, 37, 49, 56, 63, 72, 72, 72, 72, 84, 94, 93, 103, 113, 112, 111, 101];

function change_col_row_for_path(path, index_for_col_row) {
    var row_col_path = [];
    for(i in path){
        var r_c = index_for_col_row[path[i]];
        var r_c2 = [r_c[1], 11 - r_c[0]];
        var x_y = [r_c2[1] + 1, 12 - r_c2[0]];
        row_col_path.push(x_y);
    }
    return row_col_path;
}

function print_path(id, path) {
    var str = id;
    for (i in path){
        str += " (" + path[i][0] + "," + path[i][1] + ")";
    }
    return str;
}

// function final_path(path) {
    
// }

