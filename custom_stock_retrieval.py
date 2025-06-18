import os
import glob
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rasa.utils.endpoints import EndpointConfig
from rasa.core.information_retrieval import SearchResultList, InformationRetrieval, SearchResult
import os
import glob


class StockInformationRetrieval(InformationRetrieval):
    def connect(self, config: EndpointConfig) -> None:
        # Kết nối đến hệ thống tìm kiếm
        self.docs_path = config.kwargs.get("docs_path", "./docs")
        # Khởi tạo embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = []
        self._load_documents()
    
    def _load_documents(self):
        """Tải và embedding tất cả tài liệu"""
        txt_files = glob.glob(f"{self.docs_path}/**/*.txt", recursive=True)
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # Chỉ thêm file không rỗng
                        # Chia nhỏ tài liệu thành chunks
                        chunks = self._split_text(content)
                        for chunk in chunks:
                            self.documents.append({
                                'text': chunk,
                                'file_path': file_path,
                                'file_name': os.path.basename(file_path)
                            })
            except Exception as e:
                print(f"Lỗi khi đọc file {file_path}: {e}")
        
        # Tạo embeddings cho tất cả documents
        if self.documents:
            texts = [doc['text'] for doc in self.documents]
            self.embeddings = self.embedding_model.encode(texts)
    
    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """Chia text thành các chunks nhỏ"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    async def _general_search(self, query: str, top_k: int = 3) -> SearchResultList:
        """Tìm kiếm thông thường sử dụng embedding similarity"""
        if not self.documents or len(self.embeddings) == 0:
            return SearchResultList(results=[], metadata={})
        
        query_embedding = np.array(self.embedding_model.encode([query]))  # shape (1, dim)
        doc_embeddings = np.array(self.embeddings)  # shape (n_docs, dim)

        if len(doc_embeddings.shape) != 2:
            raise ValueError("Document embeddings must be a 2D array")

        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        # Lấy top_k kết quả có similarity cao nhất
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Threshold để lọc kết quả không liên quan
                doc = self.documents[idx]
                search_result = SearchResult(
                    text=doc['text'],
                    metadata={
                        "file_path": doc['file_path'],
                        "file_name": doc['file_name'],
                        "similarity_score": float(similarities[idx])
                    },
                    score=float(similarities[idx])
                )
                results.append(search_result)
        
        return SearchResultList(
            results=results, 
            metadata={
                "query": query,
                "total_documents_searched": len(self.documents),
                "search_method": "embedding_similarity"
            }
        )
    
    async def search(
        self, query: str, tracker_state: dict, threshold: float = 0.0
    ) -> SearchResultList:
        # Kiểm tra nếu câu hỏi về cổ phiếu FPT
        if "FPT" in query.upper() or "cổ phiếu FPT" in query:
            return await self._search_fpt_stock(query, tracker_state, threshold)
        
        # Tìm kiếm thông thường cho các truy vấn khác
        return await self._general_search(query)
    
    async def _search_fpt_stock(self, query: str, tracker_state: dict, threshold: float = 0.0) -> SearchResultList:
        stock_symbol = None
        for symbol in ["FPT"]:  # Có thể mở rộng với danh sách mã khác
            if symbol in query.upper():
                stock_symbol = symbol
                break

        if stock_symbol:
            return await self._search_stock_by_symbol(stock_symbol)

        # Nếu không phải cổ phiếu cụ thể, dùng phương pháp tìm kiếm chung
        return await self._general_search(query)

    async def _search_stock_by_symbol(self, symbol: str) -> SearchResultList:
        # Tìm các file txt liên quan đến mã cổ phiếu
        all_txt_files = glob.glob(f"{self.docs_path}/*.txt")

        #negative_indicators = ["tin xấu", "lỗ", "giảm", "âm", "rủi ro", "bad news", "loss", "drop", "risk", "negative"]
        negative_indicators = ["drop"]
        has_negative_news = False

        content = ""
        evidence = ""

        for file_path in all_txt_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if symbol.lower() in file_content.lower():
                    content += file_content + "\n"

                # Kiểm tra các từ ngữ tiêu cực
                for indicator in negative_indicators:
                    if indicator in file_content.lower():
                        has_negative_news = True
                        evidence = file_content.strip()[:500]  # Trích đoạn nội dung làm chứng cứ
                        break

        if not content.strip():
            result_text = f"No available information found for stock symbol {symbol}."
        elif has_negative_news:
            result_text = (
                f"The stock {symbol} shows signs of negative performance. "
                f"You should be cautious when investing.\n\nExample info:\n{content.strip()[:500]}"
            )
        else:
            result_text = (
                f"The stock {symbol} appears positive. It could be a good investment opportunity.\n\n"
                f"Example info:\n{content.strip()[:500]}"
            )

        search_result = SearchResult(
            text=result_text,
            metadata={"stock": symbol, "analysis": "custom_logic"},
            score=1.0
        )

        return SearchResultList(results=[search_result], metadata={})