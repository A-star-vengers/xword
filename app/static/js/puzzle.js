puzzleState = {
	"nrows": 6,
	"ncols": 7,
	"hints": hints,
	"hlRow": 0,
	"hlCol": 0,
	"hlDir": "across"
};

function createEmptyGrid() {
	s = puzzleState;
	var grid = s["grid"] = new Array(s.nrows);
	for(var i = 0; i < s.nrows; i++) {
		grid[i] = new Array(s.ncols);
		grid[i].fill("");
	}
}

function fillGrid() {
	s = puzzleState
	for(var i = 0; i < s.hints.length; i++) {
		hint = s.hints[i];
		r = hint.row
		c = hint.col

		for(var j = 0; j < hint.answer.length; j++) {
			if(r >= s.nrows || c >= s.ncols) {
				console.error("grid not big enough", hint.answer);
				return false;
			}

			if(s.grid[r][c] != "" && s.grid[r][c] != hint.answer[j]) {
				console.error("hint clash", hint.answer, s.grid[r][c], hint.answer[j]);
				return false;
			}
			s.grid[r][c] = hint.answer[j];

			if(hint.direction == "across") {
				c += 1;
			} else {
				r += 1;
			}
		}
	}
	return true;
}

function getLine(row, col, dir) {
	var line = [];
	var r    = (dir == "across") ? row : 0;
	var c    = (dir == "down")   ? col : 0;
	var rInc = (dir == "across") ? 0 : 1;
	var cInc = (dir == "down")   ? 0 : 1;
	var n    = (dir == "across") ? s.ncols : s.nrows;

	for(var i = 0; i < n; i++) {
		cell = getCell(r, c);
		if(!cell.classList.contains('black')) {
			line.push(cell);
		}
		r += rInc;
		c += cInc;
	}
	return line;
}

function setHighlight(newRow, newCol, newDir) {
	s = puzzleState;
	if(newRow < 0 || newRow >= s.nrows) {
		newRow = s.hlRow;
	}

	if(newCol < 0 || newCol >= s.ncols) {
		newCol = s.hlCol;
	}

	if(typeof newDir === 'undefined') {
		newDir = s.hlDir;
	}

	if(s.grid[newRow][newCol] == "") {
		newRow = s.hlRow;
		newCol = s.hlCol;
	}

	var oldLine = getLine(s.hlRow, s.hlCol, s.hlDir);
	for(var i = 0; i < oldLine.length; i++) {
		oldLine[i].classList.remove("active", "highlighted");
	}

	s.hlRow = newRow;
	s.hlCol = newCol;
	s.hlDir = newDir;

	var newLine = getLine(s.hlRow, s.hlCol, s.hlDir);
	for(var i = 0; i < newLine.length; i++) {
		newLine[i].classList.add("highlighted");
	}
	getCell(s.hlRow, s.hlCol).classList.add("active");
}

function cellClicked(r, c) {
	dir = s.hlDir;
	if(s.hlRow == r && s.hlCol == c) {
		dir = s.hlDir == "across" ? "down" : "across";
	}
	setHighlight(r, c, dir);
}

function getCell(row, col) {
	cellId = 'puzzleCell-'+row+'-'+col;
	return document.getElementById(cellId);
}

function setLetter(letter) {
	cell = getCell(s.hlRow, s.hlCol);
	cell.innerHTML = letter
	if(s.hlDir == "across") {
		setHighlight(s.hlRow, s.hlCol+1);
	} else {
		setHighlight(s.hlRow+1, s.hlCol);
	}
}

function backspace() {
	console.log('backspace');
	if(hlDir == "across") {
		setHighlight(hlRow, hlCol-1);
	} else {
		setHighlight(hlRow-1, hlCol);
	}
}

function setupKeypress() {
	body = document.getElementsByTagName('body')[0];
	body.addEventListener('keypress', function(event) {
		if(event.key == "Backspace") {
			backspace();
		} else if((event.charCode >= 65 && event.charCode <= 90)
			|| (event.charCode >= 97 && event.charCode <= 122)) {
			setLetter(event.key.toUpperCase());
		}
	});
}

function renderPuzzle() {
	table = document.createElement('table');
	table.style.height = (500*s.nrows/s.ncols)+"px";

	for(var r = 0; r < s.nrows; r++) {
		tr = document.createElement('tr');
		for(var c = 0; c < s.ncols; c++) {
			td = document.createElement('td');
			td.id = 'puzzleCell-'+r+'-'+c;
			td.style.height = (100/s.nrows)+"%";
			td.style.width = (100/s.ncols)+"%";
			td.innerHTML = "";
			if(s.grid[r][c] == "") {
				td.classList.add('black');
			} else {
				td.addEventListener('click', function(r, c) {
					return function() { cellClicked(r,c); };
				}(r,c));
			}
			tr.appendChild(td);
		}
		table.appendChild(tr);
	}
	return table;
}

function renderHints(dir) {
	s = puzzleState;
	dirHints = puzzleState.hints.filter(function(hint) {
		return hint.direction == dir;
	});

	container = document.createElement('div');

	header = document.createElement('h2');
	header.innerHTML = dir.toUpperCase();

	ol = document.createElement('ol');
	for(var i = 0; i < dirHints.length; i++) {
		li = document.createElement('li');
		li.value = dirHints[i].num;
		li.innerHTML = dirHints[i].hint;
		ol.appendChild(li);
	}

	container.appendChild(header);
	container.appendChild(ol);

	return container;
}

function setupPuzzle(target) {
	s = puzzleState;
	createEmptyGrid();
	fillGrid();

	container = document.getElementById(target);
	container.appendChild(renderPuzzle());
	container.appendChild(renderHints("across"));
	container.appendChild(renderHints("down"))

	setupKeypress();
	setHighlight(0,0);
}
