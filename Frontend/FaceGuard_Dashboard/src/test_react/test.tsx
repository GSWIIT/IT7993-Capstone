function Message() {
    const name='Minh';
  if (name === 'Minh') 
        return <h1>Message for Minh</h1>;
    return <h1>Message for {name}</h1>;
}
export default Message;