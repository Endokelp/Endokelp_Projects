import React, { useState, useEffect } from 'react';

type Player = 'X' | 'O' | null;
type Board = Player[];

interface GameState {
  board: Board;
  currentPlayer: Player;
  winner: Player;
  gameOver: boolean;
}

const TicTacToe: React.FC = () => {
  const [firstPlayer, setFirstPlayer] = useState<'X' | 'O'>('X');
  const [gameState, setGameState] = useState<GameState>({
    board: Array(9).fill(null),
    currentPlayer: 'X',
    winner: null,
    gameOver: false
  });

  const checkWinner = (board: Board): Player => {
    const lines = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
      [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
      [0, 4, 8], [2, 4, 6] // diagonals
    ];

    for (const [a, b, c] of lines) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    return null;
  };

  const isBoardFull = (board: Board): boolean => {
    return board.every(cell => cell !== null);
  };

  // Unbeatable AI strategy implementation
  const getWinningLines = () => {
    return [
      [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
      [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
      [0, 4, 8], [2, 4, 6] // diagonals
    ];
  };

  const canWin = (board: Board, player: Player): number | null => {
    const lines = getWinningLines();
    for (const line of lines) {
      const values = line.map(i => board[i]);
      if (values.filter(v => v === player).length === 2 && values.filter(v => v === null).length === 1) {
        return line[values.indexOf(null)];
      }
    }
    return null;
  };

  const findForks = (board: Board, player: Player): number[] => {
    const forks: number[] = [];
    const emptySpots = board.map((cell, index) => cell === null ? index : -1).filter(index => index !== -1);
    
    for (const spot of emptySpots) {
      const testBoard = [...board];
      testBoard[spot] = player;
      
      // Count how many ways this player can win from this position
      let winningMoves = 0;
      const lines = getWinningLines();
      
      for (const line of lines) {
        const values = line.map(i => testBoard[i]);
        if (values.filter(v => v === player).length === 2 && values.filter(v => v === null).length === 1) {
          winningMoves++;
        }
      }
      
      // If there are 2 or more ways to win, it's a fork
      if (winningMoves >= 2) {
        forks.push(spot);
      }
    }
    
    return forks;
  };

  const getOppositeCorner = (board: Board, opponent: Player): number | null => {
    const cornerPairs = [[0, 8], [2, 6]];
    
    for (const [corner1, corner2] of cornerPairs) {
      if (board[corner1] === opponent && board[corner2] === null) {
        return corner2;
      }
      if (board[corner2] === opponent && board[corner1] === null) {
        return corner1;
      }
    }
    
    return null;
  };

  const getAIMove = (board: Board): number => {
    const aiPlayer = 'O';
    const humanPlayer = 'X';
    
    // 1. Win if possible
    const winMove = canWin(board, aiPlayer);
    if (winMove !== null) return winMove;
    
    // 2. Block opponent's win
    const blockMove = canWin(board, humanPlayer);
    if (blockMove !== null) return blockMove;
    
    // 3. Create a fork
    const aiForks = findForks(board, aiPlayer);
    if (aiForks.length > 0) {
      return aiForks[0];
    }
    
    // 4. Block opponent's fork
    const opponentForks = findForks(board, humanPlayer);
    if (opponentForks.length > 0) {
      // If opponent has multiple fork opportunities, we need to force them to defend
      if (opponentForks.length === 1) {
        return opponentForks[0];
      } else {
        // Create a two-in-a-row to force opponent to block instead of creating fork
        const emptySpots = board.map((cell, index) => cell === null ? index : -1).filter(index => index !== -1);
        for (const spot of emptySpots) {
          const testBoard = [...board];
          testBoard[spot] = aiPlayer;
          if (canWin(testBoard, aiPlayer) !== null) {
            return spot;
          }
        }
        // If we can't create a threat, block one of the forks
        return opponentForks[0];
      }
    }
    
    // 5. Take center if available
    if (board[4] === null) return 4;
    
    // 6. Take opposite corner if opponent is in a corner
    const oppositeCorner = getOppositeCorner(board, humanPlayer);
    if (oppositeCorner !== null) return oppositeCorner;
    
    // 7. Take any available corner
    const corners = [0, 2, 6, 8];
    const availableCorners = corners.filter(i => board[i] === null);
    if (availableCorners.length > 0) {
      return availableCorners[0];
    }
    
    // 8. Take any available side
    const sides = [1, 3, 5, 7];
    const availableSides = sides.filter(i => board[i] === null);
    if (availableSides.length > 0) {
      return availableSides[0];
    }
    
    // Fallback: take any available spot
    const availableSpots = board.map((cell, index) => cell === null ? index : -1).filter(index => index !== -1);
    return availableSpots[0];
  };

  const handleCellClick = (index: number) => {
    if (gameState.board[index] || gameState.gameOver || gameState.currentPlayer === 'O') {
      return;
    }

    const newBoard = [...gameState.board];
    newBoard[index] = 'X';
    
    const winner = checkWinner(newBoard);
    const isGameOver = winner !== null || isBoardFull(newBoard);

    setGameState({
      board: newBoard,
      currentPlayer: isGameOver ? 'X' : 'O',
      winner,
      gameOver: isGameOver
    });
  };

  // AI move effect
  useEffect(() => {
    if (gameState.currentPlayer === 'O' && !gameState.gameOver) {
      const timer = setTimeout(() => {
        const newBoard = [...gameState.board];
        const aiMove = getAIMove(newBoard);
        newBoard[aiMove] = 'O';
        
        const winner = checkWinner(newBoard);
        const isGameOver = winner !== null || isBoardFull(newBoard);

        setGameState({
          board: newBoard,
          currentPlayer: isGameOver ? 'O' : 'X',
          winner,
          gameOver: isGameOver
        });
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [gameState.currentPlayer, gameState.gameOver, gameState.board]);

  const resetGame = () => {
    // Switch who goes first for the next game
    const nextFirstPlayer = firstPlayer === 'X' ? 'O' : 'X';
    setFirstPlayer(nextFirstPlayer);
    
    setGameState({
      board: Array(9).fill(null),
      currentPlayer: nextFirstPlayer,
      winner: null,
      gameOver: false
    });
  };

  const getStatusMessage = () => {
    if (gameState.winner === 'X') return 'You won! 🎉';
    if (gameState.winner === 'O') return 'I won! 🤖';
    if (gameState.gameOver) return "It's a draw! 🤝";
    if (gameState.currentPlayer === 'O') return 'My turn...';
    return 'Your turn';
  };

  // AI move on game start if AI goes first
  useEffect(() => {
    if (firstPlayer === 'O' && gameState.board.every(cell => cell === null) && !gameState.gameOver) {
      const timer = setTimeout(() => {
        const newBoard = [...gameState.board];
        const aiMove = getAIMove(newBoard);
        newBoard[aiMove] = 'O';
        
        const winner = checkWinner(newBoard);
        const isGameOver = winner !== null || isBoardFull(newBoard);

        setGameState({
          board: newBoard,
          currentPlayer: isGameOver ? 'O' : 'X',
          winner,
          gameOver: isGameOver
        });
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [firstPlayer, gameState.board, gameState.gameOver]);

  return (
    <div className="liquid-glass-card dark:liquid-glass-card-dark rain-behind-glass p-6 max-w-sm mx-auto relative z-20">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 text-center">
        Can you win against me?
      </h3>
      
      <div className="text-center mb-4">
        <span className={`text-sm font-medium ${
          gameState.winner === 'X' ? 'text-green-600 dark:text-green-400' :
          gameState.winner === 'O' ? 'text-red-600 dark:text-red-400' :
          'text-gray-600 dark:text-gray-400'
        }`}>
          {getStatusMessage()}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4">
        {gameState.board.map((cell, index) => (
          <button
            key={index}
            onClick={() => handleCellClick(index)}
            disabled={gameState.gameOver || cell !== null || gameState.currentPlayer === 'O'}
            className={`
              w-16 h-16 rounded-lg border-2 font-bold text-xl transition-all duration-200
              ${cell === 'X' ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-700' :
                cell === 'O' ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700' :
                'border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }
              ${gameState.currentPlayer === 'O' ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
              disabled:cursor-not-allowed disabled:opacity-50
            `}
          >
            {cell}
          </button>
        ))}
      </div>

      <button
        onClick={resetGame}
        className="w-full px-4 py-2 liquid-button dark:liquid-button-dark text-gray-900 dark:text-white font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
      >
        New Game
      </button>

      <div className="mt-3 text-xs text-gray-500 dark:text-gray-400 text-center">
        You are X, I am O
      </div>
    </div>
  );
};

export default TicTacToe;