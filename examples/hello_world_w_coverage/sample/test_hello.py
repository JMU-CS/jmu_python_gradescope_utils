import unittest
import hello_world

class TestHelloWorld(unittest.TestCase):

    def test_hello(self):
        """Test hello_func. """
        import hello_world
        self.assertEquals(hello_world.hello_func(), "Hello World")

if __name__ == "__main__":
    unittest.main()


