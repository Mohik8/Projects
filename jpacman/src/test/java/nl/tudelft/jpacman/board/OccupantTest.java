package nl.tudelft.jpacman.board;

import static org.assertj.core.api.Assertions.assertThat;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.params.*;
import org.junit.jupiter.params.provider.*;
import java.util.stream.*;
import static org.assertj.core.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test suite to confirm that {@link Unit}s correctly (de)occupy squares.
 *
 * @author Jeroen Roosen 
 *
 */
class OccupantTest {

    /**
     * The unit under test.
     */
    private Unit unit;
    private Square square;
    /**
     * Resets the unit under test.
     */
    @BeforeEach
    void setUp() {
        unit = new BasicUnit();
        square = new BasicSquare();
    }

    /**
     * Asserts that a unit has no square to start with.
     */
    @Test
    void noStartSquare() {
        unit = new BasicUnit();
        assertNull(square);
    }

    /**
     * Tests that the unit indeed has the target square as its base after
     * occupation.
     */
    @Test
    void testOccupy() {
        // Remove the following placeholder:
        unit.occupy(square);
        assertThat(unit.getSquare()).isEqualTo(square);
        assertTrue(square.getOccupants().contains(unit));
    }

    /**
     * Test that the unit indeed has the target square as its base after
     * double occupation.
     */
    @Test
    void testReoccupy() {
        Square s = new BasicSquare();
        unit.occupy(square);
        unit.occupy(s);
        assertThat(unit.getSquare()).isEqualTo(s);
        assertTrue(s.getOccupants().contains(unit));
        assertThat(square.getOccupants()).doesNotContain(unit);
    }
    @ParameterizedTest
    @ValueSource(strings = { "s1", "s2", "s3" })
    void testOccupySquares(String squareN){
        Square newSquare = new BasicSquare();
        unit.occupy(newSquare);
        assertThat(unit.getSquare()).isEqualTo(newSquare);
        assertTrue(newSquare.getOccupants().contains(unit));
    }

    @Test
    void testVacate(){
        unit.occupy(square);
        unit.leaveSquare();
        assertThat(unit.getSquare()).isNull();
        assertThat(square.getOccupants()).doesNotContain(unit);
    }

}
