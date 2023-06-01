<p>Download stanford-ner-2020-11-17<p>
<p>Download stanford-corenlp-4.5.1<p>
<p>Run the java NER server on port 9000 java -Xmx4G -cp Users/moneim/NLG_Assignment3/stanford-corenlp-4.5.1/* edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 30000 -threads 5 -maxCharLength 100000  -serverProperties corenlp_server-b7d61cffc2dc4fb9.props -preload ner<p>
<p>From inside the directory run the backend application python3 -m flask run<p>
