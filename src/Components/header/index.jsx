import React, { Component } from 'react'
import MyLink from './myLink'
import './index.css'

export default class Header extends Component {

  state = {
    isExpand: false
  }

  expandSearch = () =>{
    const isExpand = !this.state.isExpand
    if(isExpand) {
      setTimeout(()=>{ 
        this.search.style.opacity = '0'
        this.submit.style.opacity = '100'
        this.input.focus()
      },400)
    }else{
      this.search.style.opacity = '100'
      this.submit.style.opacity = '0'
    }
    this.setState({isExpand: isExpand})
  }

  render() {
    const {isExpand} = this.state
    return (
      <div className={ isExpand ? 'header-main header-main-expand' : 'header-main'}>
        <a href="#" className='header-logo'>
          <img className='logo-img' src="/img/盾牌,安全,保护.png" alt="logo" />
          <p>中国野生动物盗猎大数据平台</p>
          <p>antipoach.cn</p>
        </a>

        <div className='header-menu'>
          <div className='header-login'>
            <a href="#">联系我们</a>
            <a href="#">注册</a>
            <a href="#">登陆</a>
          </div>

          <nav className='header-nav'>
            <MyLink className='header-link' to='/' name='主页'/>
            <MyLink className='header-link' to='/charts' name='数据统计'/>
            <MyLink className='header-link' to='/search' name='高级检索'/>
            <MyLink className='header-link' to='/about' name='关于'/>
          </nav>
        </div>
        
        <svg className={ isExpand ? "search-icon search-icon-expand" : "search-icon"} 
        ref={c =>this.search = c} onClick={this.expandSearch} 
        t="1641645666827" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="24051" width="128" height="128"><path d="M453.818182 23.272727C704.465455 23.272727 907.636364 226.443636 907.636364 477.090909c0 35.746909-4.142545 70.981818-12.264728 105.192727a46.545455 46.545455 0 0 1-90.577454-21.504c6.469818-27.182545 9.751273-55.202909 9.751273-83.688727C814.545455 277.876364 653.032727 116.363636 453.818182 116.363636 254.603636 116.363636 93.090909 277.876364 93.090909 477.090909 93.090909 676.305455 254.603636 837.818182 453.818182 837.818182c101.003636 0 195.211636-41.658182 262.981818-113.826909a46.545455 46.545455 0 0 1 63.650909-3.979637c2.978909 1.792 5.818182 3.956364 8.401455 6.446546l213.201454 205.684363a45.707636 45.707636 0 0 1 0.581818 65.233455l-0.581818 0.581818a46.545455 46.545455 0 0 1-65.233454 0.581818l-185.390546-178.827636A452.305455 452.305455 0 0 1 453.818182 930.909091C203.170909 930.909091 0 727.738182 0 477.090909S203.170909 23.272727 453.818182 23.272727z m76.613818 179.828364c86.714182 23.598545 147.2 76.078545 177.245091 154.973091a46.545455 46.545455 0 0 1-86.993455 33.140363c-19.176727-50.362182-55.994182-82.315636-114.688-98.280727a46.545455 46.545455 0 1 1 24.436364-89.832727z" p-id="24052" fill="#ffffff"></path></svg>
        <span className={isExpand? 'header-search-closebtn':'header-search-closebtn-closed'} onClick={this.expandSearch} >×</span>

        <form className='header-search'>
          <input type="text" placeholder='输入物种名、地区等进行快速搜索' ref={c =>this.input = c} />
          <button type="submit">
            <svg className={ isExpand ? "search-submit" : "search-submit search-submit-closed" } ref={c =>this.submit = c} t="1641645666827" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="24051" width="128" height="128"><path d="M453.818182 23.272727C704.465455 23.272727 907.636364 226.443636 907.636364 477.090909c0 35.746909-4.142545 70.981818-12.264728 105.192727a46.545455 46.545455 0 0 1-90.577454-21.504c6.469818-27.182545 9.751273-55.202909 9.751273-83.688727C814.545455 277.876364 653.032727 116.363636 453.818182 116.363636 254.603636 116.363636 93.090909 277.876364 93.090909 477.090909 93.090909 676.305455 254.603636 837.818182 453.818182 837.818182c101.003636 0 195.211636-41.658182 262.981818-113.826909a46.545455 46.545455 0 0 1 63.650909-3.979637c2.978909 1.792 5.818182 3.956364 8.401455 6.446546l213.201454 205.684363a45.707636 45.707636 0 0 1 0.581818 65.233455l-0.581818 0.581818a46.545455 46.545455 0 0 1-65.233454 0.581818l-185.390546-178.827636A452.305455 452.305455 0 0 1 453.818182 930.909091C203.170909 930.909091 0 727.738182 0 477.090909S203.170909 23.272727 453.818182 23.272727z m76.613818 179.828364c86.714182 23.598545 147.2 76.078545 177.245091 154.973091a46.545455 46.545455 0 0 1-86.993455 33.140363c-19.176727-50.362182-55.994182-82.315636-114.688-98.280727a46.545455 46.545455 0 1 1 24.436364-89.832727z" p-id="24052" fill="#ffffff"></path></svg>
          </button>
        </form>
      </div>
    )
  }
}