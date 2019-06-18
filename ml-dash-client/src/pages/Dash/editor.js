import MonacoEditor from "react-monaco-editor";




export default function Editor() {


  return <MonacoEditor
      height="200"
      language="yaml"
      theme="vs-github"
      value={dashConfig && dashConfig.text}
      options={{selectOnLineNumbers: true, folding: true}}
      onChange={(value) => updateDashConfigText(dashConfig && dashConfig.id, value)}
      editorDidMount={() => null}/>
}

