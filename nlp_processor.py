import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import re
import string

class NLPAnomalyDetector:
    def __init__(self, anomaly_threshold=0.3):
        """
        Initialize NLP Anomaly Detector
        
        Args:
            anomaly_threshold (float): Threshold below which similarity is considered anomalous
        """
        self.anomaly_threshold = anomaly_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        self.scaler = StandardScaler()
        
    def preprocess_text(self, text):
        """
        Preprocess text for analysis
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep medical terms
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_features(self, texts):
        """
        Extract TF-IDF features from texts
        
        Args:
            texts (list): List of texts to process
            
        Returns:
            numpy.ndarray: Feature matrix
        """
        # Preprocess all texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Handle case where we have very few documents
        if len(processed_texts) <= 1:
            return np.array([[0.0]])
        
        try:
            # Fit and transform texts to TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            return tfidf_matrix.toarray()
        except ValueError:
            # Handle case where all texts are empty or very similar
            return np.ones((len(texts), 1))
    
    def calculate_similarity_metrics(self, current_text, previous_texts):
        """
        Calculate various similarity metrics between current and previous texts
        
        Args:
            current_text (str): Current case note text
            previous_texts (list): List of previous case note texts
            
        Returns:
            dict: Dictionary containing similarity metrics
        """
        all_texts = [current_text] + previous_texts
        features = self.extract_features(all_texts)
        
        if features.shape[1] == 1:  # All texts are too similar or empty
            return {
                'avg_cosine_similarity': 1.0,
                'min_cosine_similarity': 1.0,
                'max_cosine_similarity': 1.0,
                'std_cosine_similarity': 0.0,
                'length_ratio': 1.0,
                'word_count_ratio': 1.0
            }
        
        current_vector = features[0:1]  # First vector is current text
        previous_vectors = features[1:]  # Rest are previous texts
        
        # Calculate cosine similarities
        similarities = cosine_similarity(current_vector, previous_vectors)[0]
        
        # Text length analysis
        current_length = len(current_text.split())
        previous_lengths = [len(text.split()) for text in previous_texts]
        avg_previous_length = np.mean(previous_lengths) if previous_lengths else 1
        
        # Word count ratio (current vs average previous)
        length_ratio = current_length / max(avg_previous_length, 1)
        
        # Calculate unique word ratio
        current_words = set(current_text.lower().split())
        previous_words = set()
        for text in previous_texts:
            previous_words.update(text.lower().split())
        
        if previous_words:
            unique_words_ratio = len(current_words - previous_words) / len(current_words) if current_words else 0
        else:
            unique_words_ratio = 1.0
        
        return {
            'avg_cosine_similarity': np.mean(similarities),
            'min_cosine_similarity': np.min(similarities),
            'max_cosine_similarity': np.max(similarities),
            'std_cosine_similarity': np.std(similarities),
            'length_ratio': length_ratio,
            'unique_words_ratio': unique_words_ratio
        }
    
    def detect_anomaly(self, current_text, previous_texts):
        """
        Detect if current text is anomalous compared to previous texts
        
        Args:
            current_text (str): Current case note text
            previous_texts (list): List of previous case note texts
            
        Returns:
            tuple: (is_anomaly (bool), anomaly_score (float))
        """
        if not previous_texts or len(previous_texts) < 2:
            return False, 0.0
        
        # Calculate similarity metrics
        metrics = self.calculate_similarity_metrics(current_text, previous_texts)
        
        # Anomaly detection logic
        anomaly_indicators = []
        
        # 1. Low similarity to previous notes
        if metrics['avg_cosine_similarity'] < self.anomaly_threshold:
            anomaly_indicators.append(1.0 - metrics['avg_cosine_similarity'])
        
        # 2. Extreme length differences
        if metrics['length_ratio'] < 0.3 or metrics['length_ratio'] > 3.0:
            length_anomaly = abs(1.0 - metrics['length_ratio']) / 2.0
            anomaly_indicators.append(min(length_anomaly, 1.0))
        
        # 3. High unique word ratio (very different vocabulary)
        if metrics['unique_words_ratio'] > 0.7:
            anomaly_indicators.append(metrics['unique_words_ratio'])
        
        # 4. Very low minimum similarity (completely different from at least one previous note)
        if metrics['min_cosine_similarity'] < 0.1:
            anomaly_indicators.append(1.0 - metrics['min_cosine_similarity'])
        
        # Calculate overall anomaly score
        if anomaly_indicators:
            anomaly_score = np.mean(anomaly_indicators)
            is_anomaly = anomaly_score > 0.5
        else:
            anomaly_score = 0.0
            is_anomaly = False
        
        return is_anomaly, round(anomaly_score, 3)
    
    def analyze_anomaly_reasons(self, current_text, previous_texts):
        """
        Provide detailed analysis of why a text might be considered anomalous
        
        Args:
            current_text (str): Current case note text
            previous_texts (list): List of previous case note texts
            
        Returns:
            dict: Detailed analysis results
        """
        metrics = self.calculate_similarity_metrics(current_text, previous_texts)
        is_anomaly, score = self.detect_anomaly(current_text, previous_texts)
        
        reasons = []
        
        if metrics['avg_cosine_similarity'] < self.anomaly_threshold:
            reasons.append(f"Low content similarity ({metrics['avg_cosine_similarity']:.3f})")
        
        if metrics['length_ratio'] < 0.3:
            reasons.append(f"Significantly shorter than usual ({metrics['length_ratio']:.2f}x)")
        elif metrics['length_ratio'] > 3.0:
            reasons.append(f"Significantly longer than usual ({metrics['length_ratio']:.2f}x)")
        
        if metrics['unique_words_ratio'] > 0.7:
            reasons.append(f"High unique vocabulary ({metrics['unique_words_ratio']:.3f})")
        
        if metrics['min_cosine_similarity'] < 0.1:
            reasons.append(f"Very different from at least one previous note ({metrics['min_cosine_similarity']:.3f})")
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': score,
            'metrics': metrics,
            'reasons': reasons
        }

# Example usage and testing
if __name__ == "__main__":
    detector = NLPAnomalyDetector()
    
    # Test with sample case notes
    previous_notes = [
        "Patient shows improvement in mood and affect. Medication compliance is good. No adverse reactions reported. Continue current treatment plan.",
        "Patient reports feeling better today. Sleep pattern has improved. Appetite is returning to normal. Therapy sessions are productive.",
        "Mood remains stable. Patient is engaging well in group therapy. Family support is strong. No concerning behaviors observed."
    ]
    
    # Normal note (should not be flagged)
    normal_note = "Patient continues to show positive progress. Mood is stable and medication adherence is excellent. Planning discharge next week."
    
    # Anomalous note (should be flagged)
    anomalous_note = "Emergency intervention required. Patient exhibited severe agitation and required restraints. Immediate psychiatric evaluation needed."
    
    print("Testing Normal Note:")
    is_anomaly, score = detector.detect_anomaly(normal_note, previous_notes)
    print(f"Is Anomaly: {is_anomaly}, Score: {score}")
    
    print("\nTesting Anomalous Note:")
    is_anomaly, score = detector.detect_anomaly(anomalous_note, previous_notes)
    print(f"Is Anomaly: {is_anomaly}, Score: {score}")
    
    analysis = detector.analyze_anomaly_reasons(anomalous_note, previous_notes)
    print(f"Reasons: {analysis['reasons']}")

