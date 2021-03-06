// Component for the end game overlay
Vue.component('xwrd-overlay', {
    template: '<div class="overlay" v-bind:class="{\'overlay-active\': done}">\
                <div class="overlay-content">\
                  <form action="/play_puzzle" method="post">\
                    <input name="csrf_token" type="hidden" :value="csrfToken">\
                    <input name="time" type="hidden" :value="totalTime" readonly><br>\
                    <h2>You finished the puzzle in {{totalTime}} seconds!</h2><br>\
                    <span>Rating:</span>\
                    <select name="rating">\
                      <option value="1">1</option>\
                      <option value="2">2</option>\
                      <option value="3">3</option>\
                      <option value="4">4</option>\
                      <option value="5" selected>5</option>\
                    </select>\
                    <span>stars</span><br>\
                    <input type="submit" value="Submit">\
                  </form>\
                </div>\
               </div>',
    props: ['csrfToken', 'totalTime', 'done']
});

// Component for a single hint
Vue.component('xwrd-hint', {
    template: '<div>\
                 {{ hint.solved ? "✓" : "" }}\
                 {{ hint.hint }}\
               </div>',
    props: ['hint'],
});

// Component for a group of hints ("across" or "down" group)
Vue.component('xwrd-hints', {
    template: '<div>\
                 <h3>{{ direction | capitalize }}</h3>\
                 <ol>\
                   <template v-for="hint in dirHints">\
                     <li :value="hint.num">\
                       <xwrd-hint :hint="hint"></xwrd-hint>\
                     </li>\
                   </template>\
                 </ol>\
               </div>',
    props: ['grid', 'hints', 'direction'],
    computed: {
        dirHints: function() {
            return this.hints.filter(function(hint) {
                return hint.direction == this.direction;
            }.bind(this));
        }
    },
    filters: {
        capitalize: function(value) {
            value = value.toString();
            return value.charAt(0).toUpperCase() + value.slice(1);
        }
    }
});

// Component for an individual puzzle cell
Vue.component('xwrd-cell', {
    template: '<div v-if="cell.black" class="black"></div>\
               <div v-else v-on:click="onClick" class="grid-cell"\
                 v-bind:class="{ active: isActive, \
                                 highlighted: isHighlighted }">\
                   <div class="hint-num"> {{ cell.num ? cell.num : ""}}</div>\
                   <div class="hint-guess"> {{ cell.guess }}</div>\
               </div>',
    props: ['cell', 'hlRow', 'hlCol', 'hlDir'],
    computed: {
        isHighlighted: function() {
            if(this.hlDir == "across") {
                return this.cell.row == this.hlRow;
            } else {
                return this.cell.col == this.hlCol;
            }
        },
        isActive: function() {
            return (this.cell.row == this.hlRow)
                   && (this.cell.col == this.hlCol);
        }
    },
    methods: {
        onClick: function(event) {
            bus.$emit('cell-click', [this.cell.row, this.cell.col]);
        }
    }
});

// Component for a grid of cells
Vue.component('xwrd-grid', {
    template: '<div><table>\
                 <tr v-for="(row, r) in grid">\
                   <td v-for="(cell, c) in grid[r]">\
                     <xwrd-cell\
                       :cell="grid[r][c]"\
                       :hlRow="hlRow"\
                       :hlCol="hlCol"\
                       :hlDir="hlDir">\
                     </xwrd-cell>\
                   </td>\
                 </tr>\
                </table></div>',
    props: ['nrows', 'ncols', 'hlRow', 'hlCol', 'hlDir', 'grid'],
});

// Component to display the current time
Vue.component('xwrd-time', {
    template: '<div><b>Time:</b> {{ minutes | pad }}:{{ seconds | pad }} </div>',
    props: ['time'],
    computed: {
        minutes: function() {
            return Math.floor(this.time/1000/60);
        },
        seconds: function() {
            return Math.floor(this.time/1000 - this.minutes*60);
        }
    },
    filters: {
        pad: function(value) {
            if(value < 10) {
                return "0" + value.toString();
            } else {
                return value.toString();
            }
        }
    }
});

// Component to display the leaderboard
Vue.component('xwrd-leaderboard', {
    template: '<div class="leaderboard">\
                <h3>Leaderboard</h3>\
                <ol>\
                    <template v-for="entry in leaderboard">\
                        <li>\
                            {{ entry.username }}\
                            <xwrd-time :time="entry.time*1000"></xwrd-time>\
                        </li>\
                    </template>\
                </ol>\
               </div>',
    props: ['leaderboard']
});

// Component to represent the whole puzzle
Vue.component('xwrd-puzzle', {
    template: '<div>\
                <xwrd-overlay\
                  :csrfToken="csrfToken"\
                  :totalTime="totalTime"\
                  :done="done">\
                </xwrd-overlay>\
                <div \
                <div class="panels">\
                    <div class="left-panel">\
                        <xwrd-leaderboard :leaderboard="leaderboard">\
                        </xwrd-leaderboard>\
                    </div>\
                    <div class="center-panel">\
                        <xwrd-grid\
                          :nrows="nrows"\
                          :ncols="ncols"\
                          :grid="grid"\
                          :hlRow="hlRow"\
                          :hlCol="hlCol"\
                          :hlDir="hlDir">\
                        </xwrd-grid>\
                    </div>\
                    <div class="right-panel">\
                        <xwrd-time :time="timeElapsed"></xwrd-time>\
                        <div><b>Done:</b> {{ done }}</div>\
                        <xwrd-hints direction="across"\
                          :hints="hints"\
                          :grid="grid">\
                        </xwrd-hints>\
                        <xwrd-hints direction="down"\
                          :hints="hints"\
                          :grid="grid">\
                        </xwrd-hints>\
                    </div>\
                </div>\
               </div>',
    data: function() {
        var hints = [];
        for (hint of this.hintsList) {
            hints.push({
                direction: hint.direction,
                row: hint.row,
                col: hint.col,
                num: hint.num,
                answer: hint.answer,
                hint: hint.hint,
                solved: false,
            });
        }

        var grid = new Array(this.nrows);
        for(var r = 0; r < this.nrows; r++) {
            grid[r] = new Array(this.ncols);
            for(var c = 0; c < this.ncols; c++) {
                grid[r][c] = {
                    black: true,
                    num: 0,
                    row: r,
                    col: c,
                    guess: "",
                    answer: ""
                }
            }
        }

        for(let hint of hints) {
            r = hint.row;
            c = hint.col;

            grid[r][c].num = hint.num;

            for(let letter of hint.answer) {
                if(r >= this.nrows || c >= this.ncols) {
                    console.error("grid not big enough", hint.answer);
                }

                if(grid[r][c].answer != "" && grid[r][c].answer != letter) {
                    console.error("hint clash", hint.answer, grid[r][c], letter);
                }

                grid[r][c].answer = letter;
                grid[r][c].black = false;

                if(hint.direction == "across") {
                    c += 1;
                } else {
                    r += 1;
                }
            }
        }

        return {
            hlDir: "across",
            hlCol: 0,
            hlRow: 0,
            grid: grid,
            hints: hints,
            done: false,
            startTime: Date.now(),
            timeElapsed: 0,
            totalTime: 0,
        }
    },
    props: ['title', 'creator', 'authors', 'nrows', 'ncols', 'hintsList', 'csrfToken', 'leaderboard'],
    created: function() {
        bus.$on('key-press', function(event) {
            this.onKeyPress(event);
        }.bind(this));

        bus.$on('cell-click', function(event) {
            this.onCellClick(event[0], event[1]);
        }.bind(this));

        setInterval(function() {
            this.timeElapsed = Date.now() - this.startTime;
        }.bind(this), 1000);
    },
    methods: {
        onKeyPress: function(event) {
            if(event.key == "Backspace") {
                this.doBackspace();
            } else if((event.charCode >= 65 && event.charCode <= 90)
                || (event.charCode >= 97 && event.charCode <= 122)) {
                this.setLetter(event.key.toUpperCase());
            }
        },
        onCellClick: function(row, col) {
            var dir = this.hlDir;

            if(this.hlRow == row && this.hlCol == col) {
                dir = (this.hlDir == "across") ? "down" : "across";
            }

            this.setHighlight(row, col, dir);
        },
        setHighlight: function(newRow, newCol, newDir) {
            if(newRow < 0 || newRow >= this.nrows) {
                newRow = this.hlRow;
            }

            if(newCol < 0 || newCol >= this.ncols) {
                newCol = this.hlCol;
            }

            if(typeof newDir === 'undefined') {
                newDir = this.hlDir;
            }

            if(this.grid[newRow][newCol].black) {
                newRow = this.hlRow;
                newCol = this.hlCol;
            }

            this.hlRow = newRow;
            this.hlCol = newCol;
            this.hlDir = newDir;
        },
        setAndMove: function(letter, amount) {
            this.grid[this.hlRow][this.hlCol].guess = letter.toUpperCase();
            if(this.hlDir == "across") {
                this.setHighlight(this.hlRow, this.hlCol+amount);
            } else {
                this.setHighlight(this.hlRow+amount, this.hlCol);
            }
            this.checkHints();
        },
        setLetter: function(letter) {
            this.setAndMove(letter, 1);
        },
        doBackspace: function() {
            this.setAndMove("", -1);
        },
        checkHints: function() {
            var numSolved = 0;
            for(let hint of this.hints) {
                var solved = true;
                var r = hint.row;
                var c = hint.col;
                for(let letter of hint.answer) {
                    if(letter != this.grid[r][c].guess) {
                        solved = false;
                        break;
                    }
                    if(hint.direction == "across") {
                        c += 1;
                    } else {
                        r += 1;
                    }
                }
                hint.solved = solved;
                numSolved += Number(solved);
            }
            if(numSolved == this.hints.length) {
                this.done = true;
                this.totalTime = Math.floor(this.timeElapsed/1000);
            }
        }
    }
});

// Event Bus
var bus = new Vue();

// Crossword Instance
var xwrd = new Vue({
    el: '#xwrd',
    data: {
        title: puzzleData.title,
        creator: puzzleData.creator,
        authors: puzzleData.authors,
        nrows: puzzleData.nrows,
        ncols: puzzleData.ncols,
        hints: puzzleData.hints,
        leaderboard: leaderboard
    }
});

// Setup global event listener for key presses
document.addEventListener('keypress', function(event) {
    bus.$emit('key-press', event);
});
