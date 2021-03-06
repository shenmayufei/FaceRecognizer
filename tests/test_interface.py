import cv2
import glob
import unittest

from insight_face.deploy.interface import FaceSearcher


class TestInterface(unittest.TestCase):

    def setUp(self):
        self.searcher = FaceSearcher("Resnet",caffe_model_path="./output/caffe", num_layers=50, device="cuda:0")
        self.searcher.load_state('./output/res50/model_ir_se50.pth', 50)
        self.reba_set = [cv2.imread(i) for i in glob.glob("tests/assets/reba/*.jpg")]
        self.nazha_set = [cv2.imread(i) for i in glob.glob("tests/assets/nazha/*.jpg")]
        self.aligned_img = cv2.imread("tests/assets/align_face.jpg")
        self.multi_face_img = cv2.imread("tests/assets/multi_face.jpg")
        self.face_bank_dir = "tests/assets/"

    def test_embedding(self):
        self.searcher.get_embedding([self.aligned_img])

    def test_verification(self):
        result = self.searcher.verify(self.reba_set[0], self.reba_set[1])
        self.assertEqual(result, True)
        if result:
            print("Reba and reba are the same person.")

        result = self.searcher.verify(self.reba_set[0], self.nazha_set[0])
        self.assertEqual(result, False)
        if not result:
            print("Reba and nazha are different persons.")

    def test_add_face_bank(self):
        self.searcher.add_face_bank(self.face_bank_dir)

    def test_one_to_many(self):
        self.searcher.add_face_bank(self.face_bank_dir, force_reload=True, bank_name='test')
        faces, names, best_sim, _, _ = self.searcher.search(self.multi_face_img, 'test')
        for name in names:
            print("Detect %s in image." % name)

    def test_search_aligned_face(self):
        self.searcher.add_face_bank(self.face_bank_dir, force_reload=True, bank_name='test')
        faces, names, best_sim = self.searcher.search_aligned_faces([self.aligned_img], face_bank="test")
        self.assertEqual(names[0], 'reba')

    def test_recognize_and_identify_strangers(self):
        self.searcher.add_face_bank(self.face_bank_dir, force_reload=True, bank_name='test')
        aquaintance, stranger = self.searcher.recognize_and_identify_strangers(self.multi_face_img, 'test')
        self.assertEqual(aquaintance[1][0], 'reba')

    def test_match(self):
        source, target, sim = self.searcher.match(self.reba_set[0], self.multi_face_img)
        self.assertEqual(len(sim), 1)

    def test_embedding_in_the_wild(self):
        emb, boxes, landmarks = self.searcher.embedding_faces_in_the_wild(self.multi_face_img)
        self.assertEqual(emb.shape[1], 512)

    def test_identify_strangers_aligned(self):
        self.searcher.add_face_bank(self.face_bank_dir, force_reload=True, bank_name='test')
        acquaintance, stranger = self.searcher.identify_strangers_aligned([self.aligned_img], face_bank="test")

        self.assertEqual(len(acquaintance[1]), 1)
        self.assertEqual(len(stranger[1]), 0)