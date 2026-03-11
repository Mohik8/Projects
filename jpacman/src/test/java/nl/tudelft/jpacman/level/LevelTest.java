package nl.tudelft.jpacman.level;

import static org.junit.jupiter.api.Assertions.*;
import nl.tudelft.jpacman.board.Board;
import nl.tudelft.jpacman.board.BoardFactory;
import nl.tudelft.jpacman.board.Direction;
import nl.tudelft.jpacman.board.Square;
import nl.tudelft.jpacman.npc.Ghost;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import javax.print.attribute.standard.Destination;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.mockito.Mockito.*;
class LevelTest {




        @Test
        public void testPlayerGhostCollision() {
            CollisionMap collisionMap = mock(CollisionMap.class);
           Level level = new Level(mock(Board.class), new ArrayList<>(), new ArrayList<>(), collisionMap);
          Player  player = mock(Player.class);
            Ghost ghost = mock(Ghost.class);
            Square square = mock(Square.class);
            Square destination = mock(Square.class);

            when(player.hasSquare()).thenReturn(true);
            when(player.getSquare()).thenReturn(square);
            when(square.getSquareAt(Direction.EAST)).thenReturn(destination);
            when(destination.isAccessibleTo(player)).thenReturn(true);
            when(destination.getOccupants()).thenReturn(new ArrayList<>());
            level.move(player, Direction.EAST);
            verify(collisionMap).collide(player, ghost);
        }

        @Test
    public void GhostGhostCollision(){
            CollisionMap collisionMap = mock(CollisionMap.class);
            Level level = new Level(mock(Board.class), new ArrayList<>(), new ArrayList<>(), collisionMap);
            Ghost  ghost = mock(Ghost.class);
            Ghost ghost2 = mock(Ghost.class);
            Square square = mock(Square.class);
            Square destination = mock(Square.class);
            when(ghost.hasSquare()).thenReturn(true);
            when(ghost.getSquare()).thenReturn(square);
            when(square.getSquareAt(Direction.EAST)).thenReturn(destination);
            when(destination.isAccessibleTo(ghost)).thenReturn(true);
            when(destination.getOccupants()).thenReturn(List.of(ghost2));
            level.move(ghost, Direction.EAST);
            verify(collisionMap).collide(ghost, ghost2);
        }
}